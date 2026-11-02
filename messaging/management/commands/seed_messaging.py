from core.seeding import SeedCommand


class Command(SeedCommand):
    target = 'messaging'
    help = "Carga datos de messaging y sus dependencias sin duplicarlos."
