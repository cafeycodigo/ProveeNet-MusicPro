from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from catalog.models import Categoria, Producto, ProductoImagen
from companies.models import Empresa, Pais, UsuarioEmpresa


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


class SupplierCatalogTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username="proveedor")
        country = Pais.objects.create(codigo_iso="AR", nombre="Argentina")
        category = Categoria.objects.create(nombre="Audio", slug="audio")
        cls.company = Empresa.objects.create(
            pais=country,
            razon_social="Mi proveedor",
            es_proveedor=True,
            estado="activa",
        )
        other_company = Empresa.objects.create(
            pais=country,
            razon_social="Otro proveedor",
            es_proveedor=True,
            estado="activa",
        )
        UsuarioEmpresa.objects.create(
            usuario=cls.user,
            empresa=cls.company,
            rol="administrador",
        )
        cls.product = Producto.objects.create(
            empresa=cls.company,
            categoria=category,
            nombre="Micrófono",
            sku="MIC-01",
        )
        Producto.objects.create(
            empresa=other_company,
            categoria=category,
            nombre="Parlante ajeno",
            sku="PAR-01",
        )
        Producto.objects.create(
            empresa=cls.company,
            categoria=category,
            nombre="Micrófono archivado",
            sku="MIC-02",
            activo=False,
        )

    def setUp(self):
        self.client.force_login(self.user)
        session = self.client.session
        session["portal_company"] = self.company.pk
        session["portal_mode"] = "supplier"
        session.save()

    def test_catalog_lists_only_products_from_active_company(self):
        response = self.client.get(reverse("app:dashboard_catalogo"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Micrófono")
        self.assertContains(response, "Micrófono archivado")
        self.assertNotContains(response, "Parlante ajeno")
        self.assertContains(response, "Agregar producto")
        self.assertContains(
            response,
            reverse("app:catalogo_editar", kwargs={"producto_id": self.product.pk}),
        )
        self.assertContains(
            response,
            reverse("app:catalogo_eliminar", kwargs={"producto_id": self.product.pk}),
        )
        self.assertEqual(len(response.context["table_rows"]), 2)

    def test_catalog_search_finds_product_by_sku(self):
        response = self.client.get(
            reverse("app:dashboard_catalogo"),
            {"q": self.product.sku},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["table_rows"]), 1)
        self.assertEqual(response.context["table_rows"][0][0], "Micrófono")

    def product_data(self, **changes):
        data = {
            "nombre": "Interfaz de audio",
            "sku": "AUD-01",
            "categoria": self.product.categoria_id,
            "marca": "MusicPro",
            "modelo": "A1",
            "descripcion": "Interfaz para grabación.",
            "precio_referencia": "",
            "moneda": "",
            "stock": "5",
            "requiere_cotizacion": "on",
            "activo": "on",
        }
        data.update(changes)
        return data

    def test_create_product(self):
        response = self.client.post(
            reverse("app:catalogo_crear"),
            self.product_data(),
        )

        self.assertRedirects(response, reverse("app:dashboard_catalogo"))
        self.assertTrue(
            Producto.objects.filter(
                empresa=self.company,
                nombre="Interfaz de audio",
                sku="AUD-01",
            ).exists()
        )

    def test_create_rejects_duplicate_company_sku(self):
        response = self.client.post(
            reverse("app:catalogo_crear"),
            self.product_data(sku=self.product.sku),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tu empresa ya usa ese código")
        self.assertEqual(Producto.objects.filter(empresa=self.company).count(), 2)

    def test_price_requires_a_currency(self):
        response = self.client.post(
            reverse("app:catalogo_crear"),
            self.product_data(precio_referencia="1200", moneda=""),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Indica la moneda del precio")
        self.assertFalse(Producto.objects.filter(empresa=self.company, sku="AUD-01").exists())

    def test_edit_product(self):
        response = self.client.post(
            reverse("app:catalogo_editar", kwargs={"producto_id": self.product.pk}),
            self.product_data(nombre="Micrófono actualizado", sku=self.product.sku),
        )

        self.assertRedirects(response, reverse("app:dashboard_catalogo"))
        self.product.refresh_from_db()
        self.assertEqual(self.product.nombre, "Micrófono actualizado")

    def test_delete_product_requires_confirmation_and_post(self):
        url = reverse("app:catalogo_eliminar", kwargs={"producto_id": self.product.pk})
        response = self.client.get(url)

        self.assertContains(response, "Eliminar producto")
        self.assertTrue(Producto.objects.filter(pk=self.product.pk).exists())

        response = self.client.post(url)

        self.assertRedirects(response, reverse("app:dashboard_catalogo"))
        self.assertFalse(Producto.objects.filter(pk=self.product.pk).exists())

    def test_related_product_cannot_be_deleted(self):
        ProductoImagen.objects.create(
            producto=self.product,
            archivo_url="/static/producto.webp",
            orden=0,
        )

        response = self.client.post(
            reverse("app:catalogo_eliminar", kwargs={"producto_id": self.product.pk}),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.redirect_chain,
            [(reverse("app:dashboard_catalogo"), 302)],
        )
        self.assertTrue(Producto.objects.filter(pk=self.product.pk).exists())
        self.assertContains(response, "No se puede eliminar este producto")

    def test_product_from_another_company_cannot_be_edited_or_deleted(self):
        other_product = Producto.objects.get(sku="PAR-01")
        for route_name in ["catalogo_editar", "catalogo_eliminar"]:
            url = reverse(
                f"app:{route_name}",
                kwargs={"producto_id": other_product.pk},
            )
            self.assertEqual(self.client.get(url).status_code, 404)
            self.assertEqual(self.client.post(url, self.product_data()).status_code, 404)


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
