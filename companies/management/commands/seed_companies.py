from core.seeding import SeedCommand


class Command(SeedCommand):
    target = 'companies'
    help = "Carga datos de companies y sus dependencias sin duplicarlos."
