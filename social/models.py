"""Modelos del módulo social."""
from django.db import models
from django.db.models import F, Q
from django.utils import timezone


class Favorito(models.Model):
    id_favorito = models.BigAutoField(primary_key=True)
    usuario = models.ForeignKey('accounts.Usuario', on_delete=models.PROTECT, db_column='id_usuario', related_name='favorito_id_usuario_set')
    producto = models.ForeignKey('catalog.Producto', on_delete=models.PROTECT, db_column='id_producto', related_name='favorito_id_producto_set')
    fecha_creacion = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'favorito'
        constraints = [
            models.UniqueConstraint(fields=['usuario', 'producto'], name="favorito_unique_0"),
        ]

    def __str__(self):
        return f"Favorito {self.pk}"


class SeguimientoProveedor(models.Model):
    id_seguimiento = models.BigAutoField(primary_key=True)
    usuario = models.ForeignKey('accounts.Usuario', on_delete=models.PROTECT, db_column='id_usuario', related_name='seguimiento_proveedor_id_usuario_set')
    empresa = models.ForeignKey('companies.Empresa', on_delete=models.PROTECT, db_column='id_empresa', related_name='seguimiento_proveedor_id_empresa_set')
    fecha_seguimiento = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'seguimiento_proveedor'
        constraints = [
            models.UniqueConstraint(fields=['usuario', 'empresa'], name="seguimiento_proveedor_unique_0"),
        ]

    def __str__(self):
        return f"SeguimientoProveedor {self.pk}"


class Publicacion(models.Model):
    id_publicacion = models.BigAutoField(primary_key=True)
    empresa = models.ForeignKey('companies.Empresa', on_delete=models.PROTECT, db_column='id_empresa', related_name='publicacion_id_empresa_set')
    usuario_autor = models.ForeignKey('accounts.Usuario', on_delete=models.PROTECT, db_column='id_usuario_autor', related_name='publicacion_id_usuario_autor_set')
    titulo = models.CharField(max_length=180, blank=True, null=True)
    contenido = models.TextField()
    visibilidad = models.CharField(max_length=24)
    estado = models.CharField(max_length=24)
    fecha_publicacion = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'publicacion'

    def __str__(self):
        return self.titulo or "Publicacion"
