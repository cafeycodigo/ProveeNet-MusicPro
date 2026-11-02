from django.test import TestCase
from django.urls import reverse

from catalog.models import Categoria, Producto
from companies.models import Empresa, Pais


class HomeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.country = Pais.objects.create(codigo_iso="CL", nombre="Chile")
        cls.category = Categoria.objects.create(nombre="Instrumentación", slug="instrumentacion")
        cls.supplier = Empresa.objects.create(
            pais=cls.country, razon_social="Proveedor Andino", es_proveedor=True,
            estado="activa", verificada=True,
        )
        cls.product = Producto.objects.create(
            empresa=cls.supplier, categoria=cls.category, nombre="Sensor térmico", sku="ST1",
        )
        Empresa.objects.create(pais=cls.country, razon_social="Proveedor inactivo",
                               es_proveedor=True, estado="inactiva")
        Empresa.objects.create(pais=cls.country, razon_social="Comprador", estado="activa")

    def test_home_only_lists_active_suppliers(self):
        response = self.client.get(reverse("app:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Conecta con")
        self.assertContains(response, "Proveedor Andino")
        self.assertNotContains(response, "Proveedor inactivo")
        self.assertNotContains(response, "Comprador")
        self.assertEqual(response.context["result_count"], 1)

    def test_search_combines_product_country_and_category(self):
        response = self.client.get(reverse("app:home"), {
            "q": "Sensor", "pais": "cl", "categoria": "instrumentacion",
        })
        self.assertEqual(response.context["result_count"], 1)
        self.assertContains(response, "Sensor térmico")
        response = self.client.get(reverse("app:home"), {"q": "Sensor", "pais": "DE"})
        self.assertEqual(response.context["result_count"], 0)

    def test_inactive_products_are_not_searchable(self):
        self.product.activo = False
        self.product.save()
        response = self.client.get(reverse("app:home"), {"q": "Sensor"})
        self.assertEqual(response.context["result_count"], 0)

    def test_product_search_preserves_total_catalog_count(self):
        Producto.objects.create(empresa=self.supplier, categoria=self.category,
                                nombre="Otro instrumento", sku="OT2")
        response = self.client.get(reverse("app:home"), {"q": "Sensor"})
        supplier = response.context["suppliers"][0]
        self.assertEqual(supplier.product_count, 2)
        self.assertEqual(len(supplier.public_products), 2)

    def test_empty_results_offer_a_way_to_clear_filters(self):
        response = self.client.get(reverse("app:home"), {"q": "Sin coincidencias"})
        self.assertContains(response, "No encontramos proveedores")
        self.assertContains(response, "Limpiar filtros")

    def test_query_is_escaped(self):
        response = self.client.get(reverse("app:home"), {"q": "<script>alert(1)</script>"})
        self.assertNotContains(response, "<script>alert(1)</script>")
        self.assertContains(response, "&lt;script&gt;")

    def test_empty_directory_renders(self):
        Empresa.objects.update(es_proveedor=False)
        response = self.client.get(reverse("app:home"))
        self.assertContains(response, "Pronto encontrarás proveedores aquí")

    def test_local_and_international_scope_use_selected_home_country(self):
        germany = Pais.objects.create(codigo_iso="DE", nombre="Alemania")
        foreign = Empresa.objects.create(pais=germany, razon_social="Proveedor Europeo",
                                         es_proveedor=True, estado="activa")
        local = self.client.get(reverse("app:home"), {"origen": "CL", "alcance": "local"})
        self.assertEqual([item.pk for item in local.context["suppliers"]], [self.supplier.pk])
        international = self.client.get(reverse("app:home"), {
            "origen": "CL", "alcance": "internacional",
        })
        self.assertEqual([item.pk for item in international.context["suppliers"]], [foreign.pk])
        self.assertEqual(international.context["network_countries"], 2)

    def test_invalid_home_country_falls_back_to_global_scope(self):
        response = self.client.get(reverse("app:home"), {"origen": "ZZ", "alcance": "local"})
        self.assertEqual(response.context["scope"], "global")
        self.assertEqual(response.context["result_count"], 1)


class PresentationTests(TestCase):
    def test_presentation_explains_all_modules(self):
        response = self.client.get(reverse("app:presentation"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["slides"]), 11)
        for module in ["accounts", "companies", "catalog", "app", "core",
                       "messaging", "social", "collaboration", "quotations", "notifications"]:
            self.assertContains(response, module)
        self.assertContains(response, "Por completar")
        self.assertContains(response, "Descargar PPTX")

    def test_pptx_download_is_an_attachment(self):
        response = self.client.get(reverse("app:presentation_download"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("attachment", response["Content-Disposition"])
        self.assertTrue(next(iter(response.streaming_content)).startswith(b"PK"))
        response.close()
