"""Ejecución transaccional de seeders y sus dependencias."""
from importlib import import_module

from django.core.management.base import BaseCommand
from django.db import transaction


DEPENDENCIES = {'accounts': [], 'companies': ['accounts'], 'catalog': ['companies'], 'social': ['catalog'], 'messaging': ['catalog'], 'quotations': ['catalog'], 'collaboration': ['messaging'], 'notifications': ['quotations']}


def ensure(model, defaults=None, **lookup):
    return model.objects.get_or_create(defaults=defaults or {}, **lookup)[0]


@transaction.atomic
def run_seeders(target=None):
    context = {}
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

    def handle(self, *args, **options):
        run_seeders(self.target)
        self.stdout.write(self.style.SUCCESS("Datos de demostración cargados correctamente."))
