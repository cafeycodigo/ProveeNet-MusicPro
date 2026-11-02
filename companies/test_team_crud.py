from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import Empresa, Pais, UsuarioEmpresa


class TeamCrudTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.admin = User.objects.create_user(username="jefa", password="Test-123456")
        cls.person = User.objects.create_user(username="persona", email="persona@example.com")
        cls.new_person = User.objects.create_user(username="nueva", email="nueva@example.com")
        cls.superuser = User.objects.create_superuser(username="global", password="Test-123456")
        country = Pais.objects.create(codigo_iso="CL", nombre="Chile")
        cls.company = Empresa.objects.create(pais=country, razon_social="Empresa A", estado="activa")
        cls.other = Empresa.objects.create(pais=country, razon_social="Empresa B", estado="activa")
        cls.owner = UsuarioEmpresa.objects.create(usuario=cls.admin, empresa=cls.company, rol="administrador")
        cls.member = UsuarioEmpresa.objects.create(usuario=cls.person, empresa=cls.company, rol="ejecutivo")
        cls.foreign_member = UsuarioEmpresa.objects.create(usuario=cls.person, empresa=cls.other, rol="ejecutivo")

    def setUp(self):
        self.client.force_login(self.admin)

    def edit_url(self, member):
        return reverse("app:equipo_editar", kwargs={"miembro_id": member.pk})

    def delete_url(self, member):
        return reverse("app:equipo_eliminar", kwargs={"miembro_id": member.pk})

    def test_list_and_search_only_active_company_memberships(self):
        response = self.client.get(reverse("app:dashboard_equipo"), {"q": "persona"})
        self.assertEqual(list(response.context["miembros"]), [self.member])
        self.assertContains(response, "Editar")
        self.assertContains(response, "Quitar")

    def test_create_membership_without_creating_another_user(self):
        count = get_user_model().objects.count()
        response = self.client.post(reverse("app:equipo_crear"), {
            "identificador": "NUEVA@example.com", "rol": "ejecutivo", "activo": "on",
            "empresa": self.other.pk,
        })
        self.assertRedirects(response, reverse("app:dashboard_equipo"))
        self.assertTrue(UsuarioEmpresa.objects.filter(usuario=self.new_person, empresa=self.company, activo=True).exists())
        self.assertFalse(UsuarioEmpresa.objects.filter(usuario=self.new_person, empresa=self.other).exists())
        self.assertEqual(get_user_model().objects.count(), count)

    def test_duplicate_membership_shows_error(self):
        response = self.client.post(reverse("app:equipo_crear"), {
            "identificador": "persona", "rol": "ejecutivo", "activo": "on",
        })
        self.assertContains(response, "Esta cuenta ya pertenece al equipo")
        self.assertEqual(UsuarioEmpresa.objects.filter(usuario=self.person, empresa=self.company).count(), 1)

    def test_invalid_role_and_unknown_user_do_not_create_data(self):
        count = UsuarioEmpresa.objects.count()
        response = self.client.post(reverse("app:equipo_crear"), {
            "identificador": "no-existe", "rol": "superuser", "activo": "on",
        })
        self.assertContains(response, "Selecciona un rol válido")
        self.assertContains(response, "Indica el usuario o correo")
        self.assertEqual(UsuarioEmpresa.objects.count(), count)

    def test_edit_changes_membership_without_granting_platform_permissions(self):
        response = self.client.post(self.edit_url(self.member), {"rol": "administrador", "activo": "on"})
        self.assertRedirects(response, reverse("app:dashboard_equipo"))
        self.member.refresh_from_db()
        self.person.refresh_from_db()
        self.foreign_member.refresh_from_db()
        self.assertEqual(self.member.rol, "administrador")
        self.assertFalse(self.person.is_staff)
        self.assertFalse(self.person.is_superuser)
        self.assertEqual(self.foreign_member.rol, "ejecutivo")

    def test_edit_can_deactivate_another_member(self):
        self.client.post(self.edit_url(self.member), {"rol": "ejecutivo"})
        self.member.refresh_from_db()
        self.person.refresh_from_db()
        self.assertFalse(self.member.activo)
        self.assertTrue(self.person.is_active)

    def test_get_delete_only_shows_confirmation(self):
        response = self.client.get(self.delete_url(self.member))
        self.assertContains(response, "Quitar del equipo")
        self.assertTrue(UsuarioEmpresa.objects.filter(pk=self.member.pk).exists())

    def test_post_delete_keeps_user_and_other_company_membership(self):
        response = self.client.post(self.delete_url(self.member))
        self.assertRedirects(response, reverse("app:dashboard_equipo"))
        self.assertFalse(UsuarioEmpresa.objects.filter(pk=self.member.pk).exists())
        self.assertTrue(get_user_model().objects.filter(pk=self.person.pk).exists())
        self.assertTrue(UsuarioEmpresa.objects.filter(pk=self.foreign_member.pk).exists())

    def test_foreign_membership_cannot_be_read_updated_or_deleted(self):
        for url in [self.edit_url(self.foreign_member), self.delete_url(self.foreign_member)]:
            self.assertEqual(self.client.get(url).status_code, 404)
            self.assertEqual(self.client.post(url, {"rol": "administrador", "activo": "on"}).status_code, 404)

    def test_non_admin_cannot_use_any_crud_view(self):
        self.client.force_login(self.person)
        for url in [reverse("app:dashboard_equipo"), reverse("app:equipo_crear"),
                    self.edit_url(self.owner), self.delete_url(self.owner)]:
            self.assertEqual(self.client.get(url).status_code, 403)
        self.assertEqual(self.client.post(reverse("app:equipo_crear")).status_code, 403)

    def test_last_admin_cannot_be_removed_or_demoted_even_by_platform_admin(self):
        self.client.force_login(self.superuser)
        session = self.client.session
        session["portal_company"] = self.company.pk
        session.save()
        response = self.client.post(self.edit_url(self.owner), {"rol": "ejecutivo", "activo": "on"})
        self.assertContains(response, "último administrador activo")
        response = self.client.post(self.delete_url(self.owner))
        self.assertContains(response, "último administrador activo")
        self.owner.refresh_from_db()
        self.assertEqual(self.owner.rol, "administrador")

    def test_self_membership_cannot_be_removed(self):
        UsuarioEmpresa.objects.filter(pk=self.member.pk).update(rol="administrador")
        response = self.client.post(self.delete_url(self.owner))
        self.assertContains(response, "No puedes quitar tu propia membresía")
        self.assertTrue(UsuarioEmpresa.objects.filter(pk=self.owner.pk).exists())

    def test_mutations_require_csrf(self):
        protected = Client(enforce_csrf_checks=True)
        protected.force_login(self.admin)
        for url in [reverse("app:equipo_crear"), self.edit_url(self.member), self.delete_url(self.member)]:
            self.assertEqual(protected.post(url).status_code, 403)
