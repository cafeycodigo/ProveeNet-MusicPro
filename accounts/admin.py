"""Administración de accounts."""
from django.contrib import admin
from django.utils.html import format_html

from .models import PerfilUsuario


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'nacionalidad', 'avatar_url', 'vista_previa')
    search_fields = ('=id', 'usuario__username', 'nacionalidad')
    list_filter = ('nacionalidad',)
    autocomplete_fields = ('usuario',)
    list_select_related = True
    list_per_page = 50
    ordering = ('id',)
    readonly_fields = ("vista_previa",)

    @admin.display(description="Imagen")
    def vista_previa(self, obj):
        if obj and obj.avatar_url:
            return format_html('<img src="{}" alt="" width="64" height="64" style="object-fit:contain">', obj.avatar_url)
        return "—"
