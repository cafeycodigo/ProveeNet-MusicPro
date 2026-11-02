"""Modelos del módulo notifications."""
from django.db import models
from django.db.models import F, Q
from django.utils import timezone


class Notificacion(models.Model):
    id_notificacion = models.BigAutoField(primary_key=True)
    usuario = models.ForeignKey('accounts.Usuario', on_delete=models.PROTECT, db_column='id_usuario', related_name='notificacion_id_usuario_set')
    tipo = models.CharField(max_length=40)
    titulo = models.CharField(max_length=180)
    contenido = models.TextField(blank=True, null=True)
    recurso_tipo = models.CharField(max_length=40, blank=True, null=True)
    recurso_id = models.BigIntegerField(blank=True, null=True)
    leida_en = models.DateTimeField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'notificacion'

    def __str__(self):
        return self.titulo or "Notificacion"


class HistorialEstado(models.Model):
    id_historial = models.BigAutoField(primary_key=True)
    entidad_tipo = models.CharField(max_length=40)
    entidad_id = models.BigIntegerField()
    estado_anterior = models.CharField(max_length=40, blank=True, null=True)
    estado_nuevo = models.CharField(max_length=40)
    usuario = models.ForeignKey('accounts.Usuario', on_delete=models.SET_NULL, db_column='id_usuario', related_name='historial_estado_id_usuario_set', blank=True, null=True)
    fecha_cambio = models.DateTimeField(default=timezone.now)
    observacion = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'historial_estado'

    def __str__(self):
        return f"HistorialEstado {self.pk}"
