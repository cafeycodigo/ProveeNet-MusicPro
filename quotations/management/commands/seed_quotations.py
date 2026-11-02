from core.seeding import SeedCommand


class Command(SeedCommand):
    target = 'quotations'
    help = "Carga datos de quotations y sus dependencias sin duplicarlos."
