from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import Client, SimpleTestCase, TestCase
from django.urls import Resolver404, resolve, reverse

from accounts.portal import SECTION_URL_NAMES
from catalog.models import Categoria, Producto
from companies.models import Empresa, Pais, UsuarioEmpresa
from messaging.models import Conversacion, ParticipanteConversacion
from notifications.models import Notificacion
from quotations.models import Cotizacion, SolicitudCotizacion, SolicitudProveedor


class ExplicitPortalRoutesTests(SimpleTestCase):
    def test_each_section_has_its_own_named_view(self):
        for section, url_name in SECTION_URL_NAMES.items():
            with self.subTest(section=section):
                match = resolve(reverse(url_name))
                self.assertEqual(match.func.__name__, "dashboard" if section == "inicio" else section)
                self.assertEqual(match.kwargs, {})

    def test_unknown_section_does_not_match_a_generic_route(self):
        with self.assertRaises(Resolver404):
            resolve("/home/seccion-inexistente")


class PortalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.admin = User.objects.create_superuser(username="platform", password="Test-pass-123")
        cls.buyer = User.objects.create_user(username="buyer", password="Test-pass-123", first_name="Camila")
        cls.seller = User.objects.create_user(username="seller", password="Test-pass-123")
        cls.member = User.objects.create_user(username="member", password="Test-pass-123")
        cls.individual = User.objects.create_user(username="individual", password="Test-pass-123")
        cls.staff = User.objects.create_user(username="staff", password="Test-pass-123", is_staff=True)
        country = Pais.objects.create(codigo_iso="CL", nombre="Chile")
        cls.buyco = Empresa.objects.create(pais=country, razon_social="Mi compradora", estado="activa")
        cls.sellco = Empresa.objects.create(pais=country, razon_social="Mi proveedora", estado="activa",
                                           es_comprador=False, es_proveedor=True)
        cls.other = Empresa.objects.create(pais=country, razon_social="Otra compradora privada", estado="activa")
        cls.dual = Empresa.objects.create(pais=country, razon_social="Empresa dual", estado="activa", es_proveedor=True)
        cls.buyer_membership = UsuarioEmpresa.objects.create(usuario=cls.buyer, empresa=cls.buyco, rol="administrador")
        UsuarioEmpresa.objects.create(usuario=cls.buyer, empresa=cls.dual, rol="ejecutivo")
        UsuarioEmpresa.objects.create(usuario=cls.seller, empresa=cls.sellco, rol="administrador")
        UsuarioEmpresa.objects.create(usuario=cls.member, empresa=cls.buyco, rol="ejecutivo")
        cat = Categoria.objects.create(nombre="Equipo", slug="equipo")
        Producto.objects.create(empresa=cls.sellco, categoria=cat, nombre="Producto propio", sku="P1")
        Producto.objects.create(empresa=cls.other, categoria=cat, nombre="Producto privado ajeno", sku="P2", activo=False)
        for company, title in [(cls.buyco, "Solicitud propia"), (cls.other, "Solicitud ajena confidencial")]:
            rfq = SolicitudCotizacion.objects.create(empresa_compradora=company, usuario_creador=cls.buyer,
                                                     titulo=title, estado="abierta")
            invitation = SolicitudProveedor.objects.create(solicitud=rfq, empresa_proveedora=cls.sellco, estado="recibida")
            Cotizacion.objects.create(solicitud_proveedor=invitation, numero_version=1, moneda="CLP",
                                      subtotal=100, impuestos=0, costo_envio=0, total=100, estado="enviada")
        cls.conversation = Conversacion.objects.create(empresa_compradora=cls.buyco, empresa_proveedora=cls.sellco, estado="activa")
        Notificacion.objects.create(usuario=cls.buyer, tipo="demo", titulo="Aviso privado de Camila")

    def section(self, name):
        return reverse(SECTION_URL_NAMES[name])

    def test_anonymous_is_redirected_to_login(self):
        response = self.client.get(reverse("app:dashboard"))
        self.assertRedirects(response, "/login?next=/home")

    def test_login_uses_django_auth_and_redirects_to_home(self):
        response = self.client.post(reverse("accounts:login"), {"username": "buyer", "password": "Test-pass-123"})
        self.assertRedirects(response, reverse("app:dashboard"))

    def test_external_next_url_is_not_used(self):
        response = self.client.post(reverse("accounts:login"), {
            "username": "buyer", "password": "Test-pass-123", "next": "https://example.com/stolen",
        })
        self.assertRedirects(response, reverse("app:dashboard"))

    def test_invalid_login_shows_error(self):
        response = self.client.post(reverse("accounts:login"), {"username": "buyer", "password": "wrong"})
        self.assertContains(response, "El usuario o la contraseña no son correctos")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_profiles_have_different_navigation(self):
        for user, expected, absent in [
            (self.admin, "Usuarios", "Mi catálogo"), (self.buyer, "Mis favoritos", "Usuarios"),
            (self.seller, "Mi catálogo", "Mis favoritos"), (self.individual, "Comprador individual", "Mi equipo"),
        ]:
            with self.subTest(user=user.username):
                self.client.force_login(user)
                response = self.client.get(reverse("app:dashboard"))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, expected)
                self.assertNotContains(response, absent)

    def test_non_admins_cannot_access_platform_or_company_team(self):
        for user in [self.buyer, self.member, self.staff, self.individual]:
            self.client.force_login(user)
            self.assertEqual(self.client.get(self.section("usuarios")).status_code, 403)
        self.client.force_login(self.member)
        self.assertEqual(self.client.get(self.section("equipo")).status_code, 403)

    def test_buyer_cannot_read_other_company_quotes(self):
        self.client.force_login(self.buyer)
        response = self.client.get(self.section("cotizaciones"))
        self.assertContains(response, "Solicitud propia")
        self.assertNotContains(response, "Solicitud ajena confidencial")

    def test_supplier_only_sees_own_catalog(self):
        self.client.force_login(self.seller)
        response = self.client.get(self.section("catalogo"))
        self.assertContains(response, "Producto propio")
        self.assertNotContains(response, "Producto privado ajeno")

    def test_switch_rejects_an_unrelated_company(self):
        self.client.force_login(self.buyer)
        response = self.client.post(reverse("app:switch_context"), {"company": self.other.pk})
        self.assertEqual(response.status_code, 403)

    def test_switching_company_recalculates_role_and_mode(self):
        self.client.force_login(self.buyer)
        response = self.client.post(reverse("app:switch_context"), {"company": self.dual.pk, "mode": "supplier"})
        self.assertRedirects(response, reverse("app:dashboard"))
        response = self.client.get(reverse("app:dashboard"))
        self.assertEqual(response.context["ctx"].mode, "supplier")
        self.assertFalse(response.context["ctx"].is_company_admin)
        self.assertEqual(self.client.get(self.section("equipo")).status_code, 403)

    def test_revoked_membership_does_not_keep_access(self):
        self.client.force_login(self.buyer)
        self.client.post(reverse("app:switch_context"), {"company": self.buyco.pk})
        self.buyer_membership.activo = False
        self.buyer_membership.save()
        response = self.client.get(self.section("cotizaciones"))
        self.assertNotContains(response, "Solicitud propia")

    def test_conversations_require_membership_and_participation(self):
        self.client.force_login(self.member)
        response = self.client.get(self.section("mensajes"))
        self.assertEqual(len(response.context["table_rows"]), 0)
        ParticipanteConversacion.objects.create(conversacion=self.conversation, usuario=self.member)
        response = self.client.get(self.section("mensajes"))
        self.assertEqual(len(response.context["table_rows"]), 1)

    def test_notifications_are_private_even_in_same_company(self):
        self.client.force_login(self.member)
        response = self.client.get(self.section("notificaciones"))
        self.assertNotContains(response, "Aviso privado de Camila")

    def test_logout_is_post_only_and_requires_csrf(self):
        self.client.force_login(self.buyer)
        self.assertEqual(self.client.get(reverse("accounts:logout")).status_code, 405)
        protected = Client(enforce_csrf_checks=True)
        protected.force_login(self.buyer)
        self.assertEqual(protected.post(reverse("accounts:logout")).status_code, 403)
        response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(response, reverse("accounts:login"))

    def test_admin_command_preserves_existing_account(self):
        before = self.admin.password
        call_command("create_platform_admin", username="platform", stdout=StringIO())
        self.admin.refresh_from_db()
        self.assertEqual(self.admin.password, before)

    def test_every_visible_sidebar_section_is_accessible(self):
        for user in [self.admin, self.buyer, self.seller, self.member, self.individual]:
            self.client.force_login(user)
            home = self.client.get(reverse("app:dashboard"))
            for item in home.context["navigation"]:
                with self.subTest(user=user.username, section=item["key"]):
                    response = self.client.get(self.section(item["key"]))
                    self.assertEqual(response.status_code, 200)

    def test_platform_admin_can_inspect_company_space(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse("app:switch_context"), {"company": self.sellco.pk, "mode": "supplier"})
        self.assertRedirects(response, reverse("app:dashboard"))
        response = self.client.get(reverse("app:dashboard"))
        self.assertEqual(response.context["ctx"].company.pk, self.sellco.pk)
        self.assertEqual(response.context["ctx"].mode, "supplier")
        self.client.post(reverse("app:switch_context"), {"company": ""})
        response = self.client.get(reverse("app:dashboard"))
        self.assertTrue(response.context["ctx"].platform)
