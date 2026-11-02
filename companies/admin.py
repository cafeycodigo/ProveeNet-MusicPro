"""Administración de companies."""
from django.contrib import admin
from django.utils.html import format_html

from .models import Pais, Empresa, UsuarioEmpresa


@admin.register(Pais)
class PaisAdmin(admin.ModelAdmin):
    list_display = ('id_pais', 'nombre', 'codigo_iso')
    search_fields = ('=id_pais', 'codigo_iso', 'nombre')
    list_per_page = 50
    ordering = ('id_pais',)


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('id_empresa', 'razon_social', 'pais', 'es_proveedor', 'es_comprador', 'verificada', 'estado', 'vista_previa')
    search_fields = ('=id_empresa', 'pais__nombre', 'razon_social', 'nombre_comercial', 'identificacion_fiscal', 'ciudad', 'direccion', 'descripcion', 'sitio_web', 'estado')
    list_filter = ('es_proveedor', 'es_comprador', 'verificada', 'estado')
    autocomplete_fields = ('pais',)
    list_select_related = True
    list_per_page = 50
    ordering = ('id_empresa',)
    readonly_fields = ("vista_previa",)

    @admin.display(description="Imagen")
    def vista_previa(self, obj):
        if obj and obj.logo_url:
            return format_html('<img src="{}" alt="" width="64" height="64" style="object-fit:contain">', obj.logo_url)
        return "—"


@admin.register(UsuarioEmpresa)
class UsuarioEmpresaAdmin(admin.ModelAdmin):
    list_display = ('id_usuario_empresa', 'usuario', 'empresa', 'rol', 'activo')
    search_fields = ('=id_usuario_empresa', 'usuario__username', 'empresa__razon_social', 'rol')
    list_filter = ('rol', 'activo')
    autocomplete_fields = ('usuario', 'empresa')
    list_select_related = True
    list_per_page = 50
    ordering = ('id_usuario_empresa',)
