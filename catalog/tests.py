from io import StringIO
from pathlib import Path
from urllib.parse import urlparse

from django.contrib.staticfiles import finders
from django.core.management import call_command
from django.test import TestCase

from catalog.demo_assets import CATEGORY_ASSETS
from catalog.models import Producto, ProductoImagen


class DemoProductImageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_catalog", stdout=StringIO())

    def test_all_demo_products_use_the_twenty_local_images(self):
        expected = {f"/static/catalog/demo/products/{stem}-{variant:02d}.webp"
                    for _, stem in CATEGORY_ASSETS for variant in (1, 2)}
        images = list(ProductoImagen.objects.select_related("producto__categoria"))
        self.assertEqual({image.archivo_url for image in images}, expected)
        self.assertEqual(len({image.producto_id for image in images}), Producto.objects.count())
        for image in images:
            self.assertIn(image.archivo_url, expected)
            if image.producto.sku.startswith("DEMO-"):
                category_index = int(image.producto.categoria.slug.rsplit("-", 1)[1]) - 1
                self.assertIn(CATEGORY_ASSETS[category_index][1], image.archivo_url)
        for url in expected:
            path = finders.find(urlparse(url).path.removeprefix("/static/"))
            self.assertIsNotNone(path, url)
            header = Path(path).read_bytes()[:12]
            self.assertEqual(header[:4], b"RIFF")
            self.assertEqual(header[8:], b"WEBP")

    def test_reloads_replace_old_placeholders_and_keep_custom_images(self):
        original = ProductoImagen.objects.get(producto__sku="OSC-X200", orden=0)
        original.archivo_url = "https://example.com/x200.png"
        original.save(update_fields=["archivo_url"])
        custom = ProductoImagen.objects.filter(producto__sku="DEMO-001", orden=0).first()
        custom.archivo_url = "/static/custom-product.webp"
        custom.save(update_fields=["archivo_url"])
        count = ProductoImagen.objects.count()
        call_command("seed_catalog", stdout=StringIO())
        self.assertEqual(ProductoImagen.objects.count(), count)
        original.refresh_from_db()
        custom.refresh_from_db()
        self.assertEqual(original.archivo_url, "/static/catalog/demo/products/accesorios-02.webp")
        self.assertEqual(custom.archivo_url, "/static/custom-product.webp")
