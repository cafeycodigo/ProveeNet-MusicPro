"""Ejecución transaccional de seeders y sus dependencias."""
from importlib import import_module
import os

from django.apps import apps
from django.contrib.auth import get_user_model

from django.core.management.base import BaseCommand
from django.db import transaction


DEPENDENCIES = {'accounts': [], 'companies': ['accounts'], 'catalog': ['companies'], 'social': ['catalog'], 'messaging': ['catalog'], 'quotations': ['catalog'], 'collaboration': ['messaging'], 'notifications': ['quotations']}


def ensure(model, defaults=None, **lookup):
    return model.objects.get_or_create(defaults=defaults or {}, **lookup)[0]


@transaction.atomic
def run_seeders(target=None, scale=1, password=None, reset_passwords=False):
    context = {"scale": scale, "password": password or os.environ.get("SEED_DEMO_PASSWORD", "ProveeNet2026!"),
               "reset_passwords": reset_passwords}
    completed = set()

    def run(name):
        if name in completed:
            return
        for dependency in DEPENDENCIES[name]:
            run(dependency)
        context.update(import_module(f"{name}.seeders").seed(context))
        completed.add(name)

    for name in ([target] if target else DEPENDENCIES):
        run(name)
    return context


class SeedCommand(BaseCommand):
    target = None

    def add_arguments(self, parser):
        parser.add_argument("--scale", type=int, default=1, help="Multiplicador del volumen demo (1 a 10).")
        parser.add_argument("--password", help="Contraseña demo; también admite SEED_DEMO_PASSWORD.")
        parser.add_argument("--reset-passwords", action="store_true", help="Reasigna la contraseña de las cuentas demo existentes.")

    def handle(self, *args, **options):
        from django.core.management.base import CommandError
        if not 1 <= options["scale"] <= 10:
            raise CommandError("--scale debe estar entre 1 y 10.")
        run_seeders(self.target, options["scale"], options["password"], options["reset_passwords"])
        self.stdout.write(f"Usuarios: {get_user_model().objects.count()}")
        for name in DEPENDENCIES:
            for model in apps.get_app_config(name).get_models():
                self.stdout.write(f"{name}.{model.__name__}: {model.objects.count()}")
        self.stdout.write(self.style.SUCCESS("Datos de demostración cargados correctamente."))
