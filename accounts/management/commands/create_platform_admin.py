import secrets

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Crea un administrador local con contraseña aleatoria sin alterar cuentas existentes."

    def add_arguments(self, parser):
        parser.add_argument("--username", default="admin_proveenet")

    def handle(self, *args, **options):
        User = get_user_model()
        username = options["username"]
        existing = User.objects.filter(username=username).first()
        if existing:
            if not existing.is_superuser:
                raise CommandError("El usuario ya existe y no es administrador. Usa otro nombre.")
            self.stdout.write("El administrador ya existe. Se conserva su contraseña.")
            return
        password = secrets.token_urlsafe(18)
        User.objects.create_superuser(username=username, password=password,
                                      first_name="Administrador", last_name="ProveeNet")
        self.stdout.write(f"Usuario: {username}\nContraseña inicial: {password}\nAcceso: /login")
