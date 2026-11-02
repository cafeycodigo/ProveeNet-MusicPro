"""Administración de messaging."""
from django.contrib import admin

from .models import Conversacion, ParticipanteConversacion, Mensaje, ProductoCompartido, EventoConversacion


@admin.register(Conversacion)
class ConversacionAdmin(admin.ModelAdmin):
    list_display = ('id_conversacion', 'empresa_compradora', 'empresa_proveedora', 'producto_contexto', 'estado', 'fecha_creacion')
    search_fields = ('=id_conversacion', 'empresa_compradora__razon_social', 'empresa_proveedora__razon_social', 'producto_contexto__nombre', 'estado')
    list_filter = ('estado',)
    autocomplete_fields = ('empresa_compradora', 'empresa_proveedora', 'producto_contexto')
    list_select_related = True
    date_hierarchy = 'fecha_creacion'
    list_per_page = 50
    ordering = ('id_conversacion',)


@admin.register(ParticipanteConversacion)
class ParticipanteConversacionAdmin(admin.ModelAdmin):
    list_display = ('id_participante', 'conversacion', 'usuario', 'ultima_lectura')
    search_fields = ('=id_participante', 'usuario__username')
    autocomplete_fields = ('conversacion', 'usuario')
    list_select_related = True
    date_hierarchy = 'fecha_ingreso'
    list_per_page = 50
    ordering = ('id_participante',)


@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ('id_mensaje', 'conversacion', 'usuario_remitente', 'empresa_remitente', 'tipo', 'fecha_envio')
    search_fields = ('=id_mensaje', 'usuario_remitente__username', 'empresa_remitente__razon_social', 'tipo', 'contenido')
    list_filter = ('tipo',)
    autocomplete_fields = ('conversacion', 'usuario_remitente', 'empresa_remitente')
    list_select_related = True
    date_hierarchy = 'fecha_envio'
    list_per_page = 50
    ordering = ('id_mensaje',)


@admin.register(ProductoCompartido)
class ProductoCompartidoAdmin(admin.ModelAdmin):
    list_display = ('id_producto_compartido', 'conversacion', 'producto', 'usuario', 'fecha_compartido')
    search_fields = ('=id_producto_compartido', 'producto__nombre', 'usuario__username')
    autocomplete_fields = ('conversacion', 'mensaje', 'producto', 'usuario')
    list_select_related = True
    date_hierarchy = 'fecha_compartido'
    list_per_page = 50
    ordering = ('id_producto_compartido',)


@admin.register(EventoConversacion)
class EventoConversacionAdmin(admin.ModelAdmin):
    list_display = ('id_evento', 'conversacion', 'usuario', 'tipo_evento', 'fecha_evento')
    search_fields = ('=id_evento', 'usuario__username', 'tipo_evento')
    list_filter = ('tipo_evento',)
    autocomplete_fields = ('conversacion', 'usuario')
    list_select_related = True
    date_hierarchy = 'fecha_evento'
    list_per_page = 50
    ordering = ('id_evento',)
