"""Datos de ejemplo del módulo catalog."""
from datetime import timedelta
from decimal import Decimal
from django.utils import timezone
from catalog.models import Categoria, Producto, Oferta
from catalog.demo_assets import CATEGORY_ASSETS, seed_product_image
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
    seed_product_image(producto, 0, "accesorios-02", "Imagen genérica de osciloscopio digital",
                       "https://example.com/x200.png")
    ensure(Oferta, producto=producto, titulo="Oferta de demostración", defaults={
        "precio_oferta": Decimal("1100.00"), "moneda": "EUR",
        "fecha_inicio": now, "fecha_fin": now + timedelta(days=30),
    })
    categories = []
    for index, (name, _) in enumerate(CATEGORY_ASSETS):
        categories.append(ensure(Categoria, slug=f"demo-categoria-{index + 1}", defaults={
            "nombre": name, "categoria_padre": categoria if index > 5 else None, "activa": True}))
    products = []
    for company_index, company in enumerate(context["suppliers"]):
        for index in range(20):
            category = categories[index % 10]
            price = Decimal(100 + index * 75)
            item = ensure(Producto, empresa=company, sku=f"DEMO-{index + 1:03d}", defaults={
                "categoria": category, "nombre": f"{category.nombre} Serie {index + 1:02d}",
                "marca": "MusicPro Demo", "modelo": f"MP-{index + 1:03d}",
                "descripcion": f"Equipo profesional de {category.nombre.lower()} para estudio y escenarios.",
                "precio_referencia": price, "moneda": "EUR", "stock": index * 5,
                "activo": index % 9 != 0, "requiere_cotizacion": index % 2 == 0,
                "fecha_publicacion": now - timedelta(days=index + 3),
            })
            products.append(item)
            for order in range(2):
                _, asset = CATEGORY_ASSETS[index % 10]
                variant = (company_index + index // 10 + order) % 2 + 1
                seed_product_image(
                    item, order, f"{asset}-{variant:02d}",
                    f"Imagen genérica de {category.nombre.lower()}, variante {variant}",
                    f"https://catalogo.example.com/demo/{company.pk}/{index + 1}-{order}.webp",
                )
            if index % 2 == 0:
                expired = index % 4 == 0
                ensure(Oferta, producto=item, titulo="Promoción demo", defaults={
                    "precio_oferta": (price * Decimal("0.90")).quantize(Decimal("0.01")),
                    "moneda": "EUR", "fecha_inicio": now - timedelta(days=30),
                    "fecha_fin": now + timedelta(days=-1 if expired else 30), "activa": not expired})
    context["products"] = products
    return {'categoria': categoria, 'producto': producto}
