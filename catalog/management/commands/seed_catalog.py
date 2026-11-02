from core.seeding import SeedCommand


class Command(SeedCommand):
    target = 'catalog'
    help = "Carga datos de catalog y sus dependencias sin duplicarlos."
