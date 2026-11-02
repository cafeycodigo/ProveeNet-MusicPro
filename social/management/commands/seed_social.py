from core.seeding import SeedCommand


class Command(SeedCommand):
    target = 'social'
    help = "Carga datos de social y sus dependencias sin duplicarlos."
