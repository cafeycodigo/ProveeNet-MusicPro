"""Datos complementarios del usuario del sistema."""
from django.conf import settings
from django.db import models


class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="perfil",
    )
    avatar_url = models.CharField(max_length=255, blank=True)
    nacionalidad = models.CharField(
        max_length=2, blank=True, help_text="Código ISO de país de nacionalidad",
    )

    def __str__(self):
        return f"Perfil de {self.usuario}"
