"""Administración de social."""
from django.contrib import admin

from .models import Favorito, SeguimientoProveedor, Publicacion


@admin.register(Favorito)
class FavoritoAdmin(admin.ModelAdmin):
    list_display = ('id_favorito', 'usuario', 'producto', 'fecha_creacion')
    search_fields = ('=id_favorito', 'usuario__username', 'producto__nombre')
    autocomplete_fields = ('usuario', 'producto')
    list_select_related = True
    date_hierarchy = 'fecha_creacion'
    list_per_page = 50
    ordering = ('id_favorito',)


@admin.register(SeguimientoProveedor)
class SeguimientoProveedorAdmin(admin.ModelAdmin):
    list_display = ('id_seguimiento', 'usuario', 'empresa', 'fecha_seguimiento')
    search_fields = ('=id_seguimiento', 'usuario__username', 'empresa__razon_social')
    autocomplete_fields = ('usuario', 'empresa')
    list_select_related = True
    date_hierarchy = 'fecha_seguimiento'
    list_per_page = 50
    ordering = ('id_seguimiento',)


@admin.register(Publicacion)
class PublicacionAdmin(admin.ModelAdmin):
    list_display = ('id_publicacion', 'titulo', 'empresa', 'usuario_autor', 'visibilidad', 'estado', 'fecha_publicacion')
    search_fields = ('=id_publicacion', 'empresa__razon_social', 'usuario_autor__username', 'titulo', 'contenido', 'visibilidad', 'estado')
    list_filter = ('visibilidad', 'estado')
    autocomplete_fields = ('empresa', 'usuario_autor')
    list_select_related = True
    date_hierarchy = 'fecha_publicacion'
    list_per_page = 50
    ordering = ('id_publicacion',)
