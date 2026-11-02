from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(DEBUG=True, DEMO_LOGIN_ENABLED=True, DEMO_LOGIN_PASSWORD="Demo-test-123")
class DemoLoginTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.demo = get_user_model().objects.create_user(
            username="demo_comprador", email="buyer@example.com", password="Demo-test-123")

    def test_only_matching_active_demo_credentials_are_exposed(self):
        get_user_model().objects.create_user(username="private_admin", password="Demo-test-123")
        get_user_model().objects.create_user(username="demo_proveedor", password="Custom-private-password")
        response = self.client.get(reverse("accounts:login"))
        self.assertContains(response, "Accesos de demostración")
        self.assertEqual([a["username"] for a in response.context["demo_accounts"]], ["demo_comprador"])
        self.assertNotContains(response, "Custom-private-password")
        self.assertNotContains(response, "private_admin")

    @override_settings(DEBUG=False)
    def test_demo_credentials_are_never_exposed_without_debug(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertNotContains(response, "Demo-test-123")
        self.assertNotContains(response, "demo-accounts-data")

    @override_settings(DEMO_LOGIN_ENABLED=False)
    def test_demo_button_can_be_disabled(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertNotContains(response, "open-demo-access")

    def test_login_accepts_case_insensitive_email(self):
        response = self.client.post(reverse("accounts:login"), {
            "username": "BUYER@example.com", "password": "Demo-test-123"})
        self.assertRedirects(response, reverse("app:dashboard"))

    def test_duplicate_email_is_not_ambiguous_login(self):
        get_user_model().objects.create_user(username="other", email="buyer@example.com", password="Other-test-123")
        response = self.client.post(reverse("accounts:login"), {
            "username": "buyer@example.com", "password": "Demo-test-123"})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.context["demo_accounts"][0]["email"], "")

    def test_demo_command_preserves_existing_password(self):
        call_command("seed_demo_access", stdout=StringIO())
        admin = get_user_model().objects.get(username="demo_admin")
        self.assertTrue(admin.is_superuser)
        admin.set_password("My-custom-admin-password")
        admin.save()
        call_command("seed_demo_access", stdout=StringIO())
        admin.refresh_from_db()
        self.assertTrue(admin.check_password("My-custom-admin-password"))
