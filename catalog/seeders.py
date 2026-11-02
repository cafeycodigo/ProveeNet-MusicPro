"""Datos de ejemplo del módulo catalog."""
from datetime import timedelta
from decimal import Decimal
from django.utils import timezone
from catalog.models import Categoria, Producto, ProductoImagen, Oferta
from core.seeding import ensure


def seed(context):
    now = timezone.now()
    proveedor = context['proveedor']
    categoria = ensure(Categoria, nombre="Instrumentación", defaults={"activa": True, "slug": "instrumentacion"})
    if not categoria.slug:
        categoria.slug = "instrumentacion"
        categoria.save(update_fields=["slug"])
    producto = ensure(Producto, empresa=proveedor, sku="OSC-X200", defaults={
        "categoria": categoria, "nombre": "Osciloscopio X200", "marca": "TechIndustrial",
        "modelo": "X200", "descripcion": "Osciloscopio digital de demostración",
        "precio_referencia": Decimal("1200.00"), "moneda": "EUR", "stock": 25,
    })
    ensure(ProductoImagen, producto=producto, archivo_url="https://example.com/x200.png",
           defaults={"texto_alternativo": "Osciloscopio X200", "orden": 0, "es_portada": True})
    ensure(Oferta, producto=producto, titulo="Oferta de demostración", defaults={
        "precio_oferta": Decimal("1100.00"), "moneda": "EUR",
        "fecha_inicio": now, "fecha_fin": now + timedelta(days=30),
    })
    return {'categoria': categoria, 'producto': producto}
