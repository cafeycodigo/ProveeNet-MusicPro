"""Diez perfiles ficticios con retratos WebP reutilizables."""
from django.templatetags.static import static

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

from accounts.models import PerfilUsuario


# Los retratos son assets estáticos compartidos; no se copian por registro.
DEMO_USERS = [
    ("demo_comprador", "comprador@example.com", "Camila", "Rojas", "CL", "camila"),
    ("demo_proveedor", "proveedor@example.com", "Alex", "Weber", "DE", "alex"),
    ("demo_sofia", "sofia@example.com", "Sofia", "Oliveira", "BR", "sofia"),
    ("demo_mateo", "mateo@example.com", "Mateo", "García", "MX", "mateo"),
    ("demo_aiko", "aiko@example.com", "Aiko", "Tanaka", "JP", "aiko"),
    ("demo_arjun", "arjun@example.com", "Arjun", "Mehta", "IN", "arjun"),
    ("demo_amina", "amina@example.com", "Amina", "Diallo", "SN", "amina"),
    ("demo_claire", "claire@example.com", "Claire", "Martin", "FR", "claire"),
    ("demo_omar", "omar@example.com", "Omar", "Hassan", "EG", "omar"),
    ("demo_jiwoo", "jiwoo@example.com", "Jiwoo", "Kim", "KR", "jiwoo"),
]


def seed(context):
    User = get_user_model()
    users = []
    # Un hash seguro por carga para las cuentas ficticias; nunca se guarda texto plano.
    password_hash = make_password(context["password"])
    records = list(DEMO_USERS)
    for index in range(10, 100 * context["scale"]):
        _, _, nombre, apellido, nacionalidad, asset = DEMO_USERS[index % 10]
        records.append((f"demo_usuario_{index + 1:04d}", f"usuario{index + 1:04d}@example.com",
                        nombre, apellido, nacionalidad, asset))
    for username, email, nombre, apellido, nacionalidad, asset in records:
        user, created = User.objects.get_or_create(username=username, defaults={
            "email": email, "first_name": nombre, "last_name": apellido,
        })
        if created or not user.has_usable_password() or context["reset_passwords"]:
            user.password = password_hash
            user.save(update_fields=["password"])
        elif not user.last_name:
            user.last_name = apellido
            user.save(update_fields=["last_name"])
        defaults = {
            "nacionalidad": nacionalidad,
            "avatar_url": static(f"accounts/demo/{asset}.webp"),
        }
        profile, _ = PerfilUsuario.objects.get_or_create(usuario=user, defaults=defaults)
        missing = [field for field in defaults if not getattr(profile, field)]
        for field in missing:
            setattr(profile, field, defaults[field])
        if missing:
            profile.save(update_fields=missing)
        users.append(user)
    return {"users": users, "buyer": users[0], "seller": users[1]}
