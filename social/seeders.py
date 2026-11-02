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
    return {}
