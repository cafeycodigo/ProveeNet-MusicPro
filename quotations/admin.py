"""Administración de quotations."""
from django.contrib import admin

from .models import SolicitudCotizacion, SolicitudDetalle, SolicitudProveedor, Cotizacion, CotizacionDetalle, OrdenCompra


@admin.register(SolicitudCotizacion)
class SolicitudCotizacionAdmin(admin.ModelAdmin):
    list_display = ('id_solicitud', 'titulo', 'empresa_compradora', 'usuario_creador', 'estado', 'fecha_solicitud', 'fecha_limite')
    search_fields = ('=id_solicitud', 'empresa_compradora__razon_social', 'usuario_creador__username', 'titulo', 'descripcion', 'estado')
    list_filter = ('estado',)
    autocomplete_fields = ('empresa_compradora', 'usuario_creador')
    list_select_related = True
    date_hierarchy = 'fecha_solicitud'
    list_per_page = 50
    ordering = ('id_solicitud',)


@admin.register(SolicitudDetalle)
class SolicitudDetalleAdmin(admin.ModelAdmin):
    list_display = ('id_detalle', 'solicitud', 'producto', 'cantidad', 'unidad_medida')
    search_fields = ('=id_detalle', 'solicitud__titulo', 'producto__nombre', 'descripcion_producto', 'unidad_medida')
    autocomplete_fields = ('solicitud', 'producto')
    list_select_related = True
    list_per_page = 50
    ordering = ('id_detalle',)


@admin.register(SolicitudProveedor)
class SolicitudProveedorAdmin(admin.ModelAdmin):
    list_display = ('id_solicitud_proveedor', 'solicitud', 'empresa_proveedora', 'estado', 'fecha_invitacion')
    search_fields = ('=id_solicitud_proveedor', 'solicitud__titulo', 'empresa_proveedora__razon_social', 'estado')
    list_filter = ('estado',)
    autocomplete_fields = ('solicitud', 'empresa_proveedora')
    list_select_related = True
    date_hierarchy = 'fecha_invitacion'
    list_per_page = 50
    ordering = ('id_solicitud_proveedor',)


@admin.register(Cotizacion)
class CotizacionAdmin(admin.ModelAdmin):
    list_display = ('id_cotizacion', 'solicitud_proveedor', 'numero_version', 'moneda', 'total', 'estado', 'fecha_emision')
    search_fields = ('=id_cotizacion', 'moneda', 'condiciones', 'estado')
    list_filter = ('moneda', 'estado')
    autocomplete_fields = ('solicitud_proveedor',)
    list_select_related = True
    date_hierarchy = 'fecha_emision'
    list_per_page = 50
    ordering = ('id_cotizacion',)


@admin.register(CotizacionDetalle)
class CotizacionDetalleAdmin(admin.ModelAdmin):
    list_display = ('id_cotizacion_detalle', 'cotizacion', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    search_fields = ('=id_cotizacion_detalle', 'producto__nombre', 'descripcion')
    autocomplete_fields = ('cotizacion', 'solicitud_detalle', 'producto')
    list_select_related = True
    list_per_page = 50
    ordering = ('id_cotizacion_detalle',)


@admin.register(OrdenCompra)
class OrdenCompraAdmin(admin.ModelAdmin):
    list_display = ('id_orden', 'numero_orden', 'cotizacion', 'total', 'moneda', 'estado', 'fecha_emision')
    search_fields = ('=id_orden', 'numero_orden', 'estado', 'moneda')
    list_filter = ('estado', 'moneda')
    autocomplete_fields = ('cotizacion',)
    list_select_related = True
    date_hierarchy = 'fecha_emision'
    list_per_page = 50
    ordering = ('id_orden',)
