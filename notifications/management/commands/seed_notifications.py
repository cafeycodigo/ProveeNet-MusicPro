from core.seeding import SeedCommand


class Command(SeedCommand):
    target = 'notifications'
    help = "Carga datos de notifications y sus dependencias sin duplicarlos."
