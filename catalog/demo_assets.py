"""Imágenes genéricas compartidas por los productos ficticios."""
from django.templatetags.static import static

from catalog.models import ProductoImagen


CATEGORY_ASSETS = [
    ("Guitarras", "guitarras"), ("Teclados", "teclados"),
    ("Baterías", "baterias"), ("Micrófonos", "microfonos"),
    ("Interfaces", "interfaces"), ("Monitores", "monitores"),
    ("Mezcladoras", "mezcladoras"), ("Amplificadores", "amplificadores"),
    ("Iluminación", "iluminacion"), ("Accesorios", "accesorios"),
]


def seed_product_image(product, order, asset, description, legacy_url):
    """Completa imágenes demo y sustituye solo el placeholder conocido."""
    url = static(f"catalog/demo/products/{asset}.webp")
    image, _ = ProductoImagen.objects.get_or_create(
        producto=product, orden=order,
        defaults={"archivo_url": url, "texto_alternativo": description,
                  "es_portada": order == 0},
    )
    if not image.archivo_url or image.archivo_url == legacy_url:
        image.archivo_url = url
        image.texto_alternativo = description
        image.save(update_fields=["archivo_url", "texto_alternativo"])
    return image
