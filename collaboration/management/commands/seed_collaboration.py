from core.seeding import SeedCommand


class Command(SeedCommand):
    target = 'collaboration'
    help = "Carga datos de collaboration y sus dependencias sin duplicarlos."
