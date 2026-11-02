"""Administración de catalog."""
from django.contrib import admin
from django.utils.html import format_html

from .models import Categoria, Producto, ProductoImagen, Oferta


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id_categoria', 'nombre', 'slug', 'categoria_padre', 'activa')
    search_fields = ('=id_categoria', 'categoria_padre__nombre', 'nombre', 'slug')
    list_filter = ('activa',)
    autocomplete_fields = ('categoria_padre',)
    list_select_related = True
    list_per_page = 50
    ordering = ('id_categoria',)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id_producto', 'nombre', 'sku', 'empresa', 'categoria', 'precio_referencia', 'moneda', 'stock', 'activo')
    search_fields = ('=id_producto', 'empresa__razon_social', 'categoria__nombre', 'nombre', 'sku', 'marca', 'modelo', 'descripcion', 'moneda')
    list_filter = ('moneda', 'requiere_cotizacion', 'activo')
    autocomplete_fields = ('empresa', 'categoria')
    list_select_related = True
    date_hierarchy = 'fecha_publicacion'
    list_per_page = 50
    ordering = ('id_producto',)


@admin.register(ProductoImagen)
class ProductoImagenAdmin(admin.ModelAdmin):
    list_display = ('id_imagen', 'producto', 'orden', 'es_portada', 'vista_previa')
    search_fields = ('=id_imagen', 'producto__nombre', 'texto_alternativo')
    list_filter = ('es_portada',)
    autocomplete_fields = ('producto',)
    list_select_related = True
    list_per_page = 50
    ordering = ('id_imagen',)
    readonly_fields = ("vista_previa",)

    @admin.display(description="Imagen")
    def vista_previa(self, obj):
        if obj and obj.archivo_url:
            return format_html('<img src="{}" alt="" width="64" height="64" style="object-fit:contain">', obj.archivo_url)
        return "—"


@admin.register(Oferta)
class OfertaAdmin(admin.ModelAdmin):
    list_display = ('id_oferta', 'titulo', 'producto', 'precio_oferta', 'moneda', 'fecha_inicio', 'fecha_fin', 'activa')
    search_fields = ('=id_oferta', 'producto__nombre', 'titulo', 'moneda')
    list_filter = ('moneda', 'activa')
    autocomplete_fields = ('producto',)
    list_select_related = True
    date_hierarchy = 'fecha_inicio'
    list_per_page = 50
    ordering = ('id_oferta',)
