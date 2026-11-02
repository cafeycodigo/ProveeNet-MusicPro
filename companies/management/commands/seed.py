from core.seeding import SeedCommand


class Command(SeedCommand):
    help = "Carga los seeders de todas las aplicaciones sin duplicar datos."
