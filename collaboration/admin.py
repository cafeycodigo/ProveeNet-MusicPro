"""Administración de collaboration."""
from django.contrib import admin

from .models import SesionCatalogo, ParticipanteSesionCatalogo, EventoCatalogo, Llamada, ParticipanteLlamada


@admin.register(SesionCatalogo)
class SesionCatalogoAdmin(admin.ModelAdmin):
    list_display = ('id_sesion', 'conversacion', 'usuario_iniciador', 'producto_actual', 'estado', 'fecha_inicio', 'fecha_fin')
    search_fields = ('=id_sesion', 'usuario_iniciador__username', 'producto_actual__nombre', 'estado')
    list_filter = ('estado',)
    autocomplete_fields = ('conversacion', 'usuario_iniciador', 'producto_actual')
    list_select_related = True
    list_per_page = 50
    ordering = ('id_sesion',)


@admin.register(ParticipanteSesionCatalogo)
class ParticipanteSesionCatalogoAdmin(admin.ModelAdmin):
    list_display = ('id_participante_sesion', 'sesion', 'usuario', 'consentimiento', 'fecha_union', 'fecha_salida')
    search_fields = ('=id_participante_sesion', 'usuario__username')
    list_filter = ('consentimiento',)
    autocomplete_fields = ('sesion', 'usuario')
    list_select_related = True
    list_per_page = 50
    ordering = ('id_participante_sesion',)


@admin.register(EventoCatalogo)
class EventoCatalogoAdmin(admin.ModelAdmin):
    list_display = ('id_evento_catalogo', 'sesion', 'usuario', 'producto', 'tipo_evento', 'fecha_evento')
    search_fields = ('=id_evento_catalogo', 'usuario__username', 'producto__nombre', 'tipo_evento')
    list_filter = ('tipo_evento',)
    autocomplete_fields = ('sesion', 'usuario', 'producto')
    list_select_related = True
    date_hierarchy = 'fecha_evento'
    list_per_page = 50
    ordering = ('id_evento_catalogo',)


@admin.register(Llamada)
class LlamadaAdmin(admin.ModelAdmin):
    list_display = ('id_llamada', 'conversacion', 'usuario_iniciador', 'tipo', 'estado', 'fecha_invitacion')
    search_fields = ('=id_llamada', 'usuario_iniciador__username', 'tipo', 'estado')
    list_filter = ('tipo', 'estado')
    autocomplete_fields = ('conversacion', 'usuario_iniciador')
    list_select_related = True
    date_hierarchy = 'fecha_invitacion'
    list_per_page = 50
    ordering = ('id_llamada',)


@admin.register(ParticipanteLlamada)
class ParticipanteLlamadaAdmin(admin.ModelAdmin):
    list_display = ('id_participante_llamada', 'llamada', 'usuario', 'estado', 'fecha_union', 'fecha_salida')
    search_fields = ('=id_participante_llamada', 'usuario__username', 'estado')
    list_filter = ('estado',)
    autocomplete_fields = ('llamada', 'usuario')
    list_select_related = True
    list_per_page = 50
    ordering = ('id_participante_llamada',)
