"""Datos de ejemplo del módulo accounts."""
from accounts.models import Usuario
from core.seeding import ensure


def seed(context):
    users = []
    for username, email, nombre in [
        ("demo_comprador", "comprador@example.com", "Camila"),
        ("demo_proveedor", "proveedor@example.com", "Alex"),
    ]:
        user, created = Usuario.objects.get_or_create(
            username=username, defaults={"email": email, "first_name": nombre},
        )
        if created:
            user.set_unusable_password()
            user.save(update_fields=["password"])
        users.append(user)
    buyer, seller = users
    return {'users': users, 'buyer': buyer, 'seller': seller}
