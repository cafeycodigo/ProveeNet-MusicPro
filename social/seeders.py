"""Datos de ejemplo del módulo social."""
from social.models import Favorito, SeguimientoProveedor, Publicacion
from core.seeding import ensure


def seed(context):
    buyer = context['buyer']
    seller = context['seller']
    proveedor = context['proveedor']
    producto = context['producto']
    ensure(Favorito, usuario=buyer, producto=producto)
    ensure(SeguimientoProveedor, usuario=buyer, empresa=proveedor)
    ensure(Publicacion, empresa=proveedor, titulo="Nuevo catálogo", defaults={
        "usuario_autor": seller, "contenido": "Conoce nuestros instrumentos.",
        "visibilidad": "publica", "estado": "publicada",
    })
    for index, user in enumerate(context["users"]):
        for offset in range(5):
            item = context["products"][(index * 7 + offset) % len(context["products"])]
            ensure(Favorito, usuario=user, producto=item)
            ensure(SeguimientoProveedor, usuario=user, empresa=item.empresa)
    for company in context["suppliers"]:
        author = context["teams"][company.pk][0]
        for index in range(5):
            ensure(Publicacion, empresa=company, titulo=f"Novedades demo {index + 1}", defaults={
                "usuario_autor": author, "contenido": f"Conoce la nueva selección profesional de {company.razon_social}. Consulta disponibilidad, garantías y entregas.",
                "visibilidad": "publica", "estado": "borrador" if index == 4 else "publicada"})
    return {}
