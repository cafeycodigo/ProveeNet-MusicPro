"""Administración de notifications."""
from django.contrib import admin

from .models import Notificacion, HistorialEstado


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('id_notificacion', 'usuario', 'tipo', 'titulo', 'fecha_creacion', 'leida_en')
    search_fields = ('=id_notificacion', 'usuario__username', 'tipo', 'titulo', 'contenido', 'recurso_tipo')
    list_filter = ('tipo',)
    autocomplete_fields = ('usuario',)
    list_select_related = True
    date_hierarchy = 'fecha_creacion'
    list_per_page = 50
    ordering = ('id_notificacion',)


@admin.register(HistorialEstado)
class HistorialEstadoAdmin(admin.ModelAdmin):
    list_display = ('id_historial', 'entidad_tipo', 'entidad_id', 'estado_anterior', 'estado_nuevo', 'usuario', 'fecha_cambio')
    search_fields = ('=id_historial', 'entidad_tipo', 'estado_anterior', 'estado_nuevo', 'usuario__username', 'observacion')
    list_filter = ('entidad_tipo',)
    autocomplete_fields = ('usuario',)
    list_select_related = True
    date_hierarchy = 'fecha_cambio'
    list_per_page = 50
    ordering = ('id_historial',)
