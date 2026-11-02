from io import StringIO
from pathlib import Path

from django.contrib.staticfiles import finders
from django.core.management import call_command
from django.test import TestCase

from companies.demo_branding import COMPANY_BRANDS, seed_brand_logo
from companies.models import Empresa


class CompanyBrandingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_companies", stdout=StringIO())

    def test_each_brand_uses_its_own_local_logo(self):
        urls = set()
        for name, asset in COMPANY_BRANDS:
            companies = Empresa.objects.filter(razon_social__startswith=name + " Demo ")
            self.assertTrue(companies.exists(), name)
            expected = f"/static/companies/demo/{asset}.webp"
            for company in companies:
                self.assertEqual(company.logo_url, expected)
                urls.add(company.logo_url)
            path = finders.find(f"companies/demo/{asset}.webp")
            self.assertIsNotNone(path, asset)
            header = Path(path).read_bytes()[:12]
            self.assertEqual(header[:4], b"RIFF")
            self.assertEqual(header[8:], b"WEBP")
        self.assertEqual(len(urls), 10)
        self.assertEqual(Empresa.objects.values("logo_url").distinct().count(), 12)

    def test_old_generic_logos_are_replaced_without_changing_custom_logos(self):
        company = Empresa.objects.get(razon_social="Sakura Audio Demo 005")
        company.logo_url = "/static/companies/demo/industrial-minera.webp"
        company.save(update_fields=["logo_url"])
        seed_brand_logo(company, "sakura-audio")
        self.assertEqual(company.logo_url, "/static/companies/demo/sakura-audio.webp")
        company.logo_url = "/static/custom-sakura.webp"
        company.save(update_fields=["logo_url"])
        count = Empresa.objects.count()
        call_command("seed_companies", stdout=StringIO())
        company.refresh_from_db()
        self.assertEqual(company.logo_url, "/static/custom-sakura.webp")
        self.assertEqual(Empresa.objects.count(), count)
