from core.seeding import SeedCommand


class Command(SeedCommand):
    target = 'accounts'
    help = "Carga datos de accounts y sus dependencias sin duplicarlos."
