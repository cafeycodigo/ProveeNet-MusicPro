from io import StringIO
from pathlib import Path
from urllib.parse import urlparse

from django.contrib.staticfiles import finders
from django.core.management import call_command
from django.test import TestCase

from django.contrib.auth import get_user_model
from accounts.models import PerfilUsuario

Usuario = get_user_model()
from companies.models import Empresa, UsuarioEmpresa


class DemoImageTests(TestCase):
    def assert_webp(self, url):
        asset = urlparse(url).path.removeprefix("/static/")
        path = finders.find(asset)
        self.assertIsNotNone(path, asset)
        header = Path(path).read_bytes()[:12]
        self.assertEqual(header[:4], b"RIFF")
        self.assertEqual(header[8:], b"WEBP")

    def test_ten_profiles_and_company_logos_are_available_locally(self):
        call_command("seed_companies", stdout=StringIO())
        self.assertEqual(Usuario.objects.count(), 100)
        self.assertEqual(PerfilUsuario.objects.values("nacionalidad").distinct().count(), 10)
        self.assertGreaterEqual(UsuarioEmpresa.objects.count(), 100)
        for user in Usuario.objects.all():
            self.assert_webp(user.perfil.avatar_url)
        for company in Empresa.objects.all():
            self.assert_webp(company.logo_url)

    def test_existing_profiles_are_completed_without_overwriting_custom_images(self):
        user = Usuario.objects.create_user(
            username="demo_comprador", email="custom@example.com",
            first_name="Personalizado", password="existing-password",
        )
        PerfilUsuario.objects.create(usuario=user, avatar_url="/static/custom.webp")
        call_command("seed_accounts", stdout=StringIO())
        user.refresh_from_db()
        self.assertTrue(user.check_password("existing-password"))
        self.assertEqual(user.email, "custom@example.com")
        self.assertEqual(user.first_name, "Personalizado")
        self.assertEqual(user.perfil.avatar_url, "/static/custom.webp")
        self.assertEqual(user.perfil.nacionalidad, "CL")
        self.assertEqual(user.last_name, "Rojas")


    def test_demo_passwords_upgrade_unusable_accounts_and_reset_only_when_requested(self):
        user = Usuario.objects.create_user(username="demo_proveedor", password=None)
        call_command("seed_accounts", password="DemoPassword2026!", stdout=StringIO())
        user.refresh_from_db()
        self.assertTrue(user.check_password("DemoPassword2026!"))
        self.assertTrue(Usuario.objects.get(username="demo_comprador").check_password("DemoPassword2026!"))
        call_command("seed_accounts", password="OtraPassword2026!", stdout=StringIO())
        user.refresh_from_db()
        self.assertTrue(user.check_password("DemoPassword2026!"))
        call_command("seed_accounts", password="OtraPassword2026!", reset_passwords=True, stdout=StringIO())
        user.refresh_from_db()
        self.assertTrue(user.check_password("OtraPassword2026!"))
