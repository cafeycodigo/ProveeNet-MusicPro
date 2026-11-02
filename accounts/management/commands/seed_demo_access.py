from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Completa los accesos ficticios del modal local sin modificar cuentas existentes."

    def handle(self, *args, **options):
        if not settings.DEBUG or not settings.DEMO_LOGIN_ENABLED:
            raise CommandError("Los accesos de demostración solo se crean en desarrollo.")
        User = get_user_model()
        for username, name, admin in [("demo_admin", "Administrador demo", True),
                                       ("demo_individual", "Comprador personal", False)]:
            if User.objects.filter(username=username).exists():
                self.stdout.write(f"{username}: cuenta existente conservada.")
                continue
            User.objects.create_user(
                username=username, email=f"{username}@example.com", first_name=name,
                password=settings.DEMO_LOGIN_PASSWORD, is_staff=admin, is_superuser=admin,
            )
            self.stdout.write(f"{username}: acceso ficticio creado.")
        self.stdout.write("Comprador y proveedor usan las cuentas existentes del comando seed.")
