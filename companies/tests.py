from io import StringIO

from django.apps import apps
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import TestCase

from messaging.models import Conversacion
from catalog.models import Producto
from accounts.models import Usuario
from companies.models import UsuarioEmpresa


class SeedTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed", stdout=StringIO())

    def test_seed_is_repeatable_and_preserves_existing_data(self):
        models = [model for name in ['accounts', 'companies', 'catalog', 'social', 'messaging', 'quotations', 'collaboration', 'notifications']
                  for model in apps.get_app_config(name).get_models()]
        counts = {model: model.objects.count() for model in models}
        product = Producto.objects.get(sku="OSC-X200")
        product.nombre = "Nombre personalizado"
        product.save()
        call_command("seed", stdout=StringIO())
        self.assertEqual(counts, {model: model.objects.count() for model in models})
        product.refresh_from_db()
        self.assertEqual(product.nombre, "Nombre personalizado")
        for model in models:
            self.assertGreater(model.objects.count(), 0, model.__name__)
            for instance in model.objects.all():
                instance.full_clean()
        for user in Usuario.objects.all():
            self.assertFalse(user.has_usable_password())

    def test_database_rejects_invalid_stock_and_duplicate_membership(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Producto.objects.update(stock=-1)
        membership = UsuarioEmpresa.objects.first()
        with self.assertRaises(IntegrityError), transaction.atomic():
            UsuarioEmpresa.objects.create(usuario=membership.usuario,
                                          empresa=membership.empresa, rol="ejecutivo")

    def test_conversation_requires_different_companies(self):
        conversation = Conversacion.objects.first()
        with self.assertRaises(IntegrityError), transaction.atomic():
            Conversacion.objects.filter(pk=conversation.pk).update(
                empresa_proveedora=conversation.empresa_compradora,
            )

class IndividualSeederTests(TestCase):
    def test_each_command_runs_on_empty_database_and_is_repeatable(self):
        names = ["accounts", "companies", "catalog", "social", "messaging",
                 "quotations", "collaboration", "notifications"]
        models = [model for name in names
                  for model in apps.get_app_config(name).get_models()]
        for name in names:
            with self.subTest(app=name), transaction.atomic():
                self.assertEqual(Usuario.objects.count(), 0)
                call_command(f"seed_{name}", stdout=StringIO())
                for model in apps.get_app_config(name).get_models():
                    self.assertGreater(model.objects.count(), 0, model.__name__)
                    for instance in model.objects.all():
                        instance.full_clean()
                counts = {model: model.objects.count() for model in models}
                call_command(f"seed_{name}", stdout=StringIO())
                self.assertEqual(counts, {model: model.objects.count() for model in models})
                transaction.set_rollback(True)
