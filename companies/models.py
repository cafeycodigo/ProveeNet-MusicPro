"""Modelos del módulo companies."""
from django.db import models
from django.db.models import F, Q
from django.utils import timezone


class Pais(models.Model):
    id_pais = models.BigAutoField(primary_key=True)
    codigo_iso = models.CharField(max_length=2, unique=True)
    nombre = models.CharField(max_length=120)

    class Meta:
        db_table = 'pais'

    def __str__(self):
        return self.nombre or "Pais"


class Empresa(models.Model):
    id_empresa = models.BigAutoField(primary_key=True)
    pais = models.ForeignKey('companies.Pais', on_delete=models.PROTECT, db_column='id_pais', related_name='empresa_id_pais_set')
    razon_social = models.CharField(max_length=180)
    nombre_comercial = models.CharField(max_length=180, blank=True, null=True)
    identificacion_fiscal = models.CharField(max_length=80, blank=True, null=True)
    ciudad = models.CharField(max_length=120, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    logo_url = models.TextField(blank=True, null=True)
    sitio_web = models.TextField(blank=True, null=True)
    es_proveedor = models.BooleanField(default=False)
    es_comprador = models.BooleanField(default=True)
    verificada = models.BooleanField(default=False)
    estado = models.CharField(max_length=24)

    class Meta:
        db_table = 'empresa'

    def __str__(self):
        return self.razon_social or "Empresa"


class UsuarioEmpresa(models.Model):
    id_usuario_empresa = models.BigAutoField(primary_key=True)
    usuario = models.ForeignKey('accounts.Usuario', on_delete=models.PROTECT, db_column='id_usuario', related_name='usuario_empresa_id_usuario_set')
    empresa = models.ForeignKey('companies.Empresa', on_delete=models.PROTECT, db_column='id_empresa', related_name='usuario_empresa_id_empresa_set')
    rol = models.CharField(max_length=32)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'usuario_empresa'
        constraints = [
            models.UniqueConstraint(fields=['usuario', 'empresa'], name="usuario_empresa_unique_0"),
        ]

    def __str__(self):
        return f"UsuarioEmpresa {self.pk}"
