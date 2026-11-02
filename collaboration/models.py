from django.conf import settings
"""Modelos del módulo collaboration."""
from django.db import models
from django.db.models import F, Q
from django.utils import timezone


class SesionCatalogo(models.Model):
    id_sesion = models.BigAutoField(primary_key=True)
    conversacion = models.ForeignKey('messaging.Conversacion', on_delete=models.PROTECT, db_column='id_conversacion', related_name='sesion_catalogo_id_conversacion_set')
    usuario_iniciador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, db_column='id_usuario_iniciador', related_name='sesion_catalogo_id_usuario_iniciador_set')
    producto_actual = models.ForeignKey('catalog.Producto', on_delete=models.SET_NULL, db_column='id_producto_actual', related_name='sesion_catalogo_id_producto_actual_set', blank=True, null=True)
    estado = models.CharField(max_length=24)
    fecha_inicio = models.DateTimeField(blank=True, null=True)
    fecha_fin = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'sesion_catalogo'

    def __str__(self):
        return f"SesionCatalogo {self.pk}"


class ParticipanteSesionCatalogo(models.Model):
    id_participante_sesion = models.BigAutoField(primary_key=True)
    sesion = models.ForeignKey('collaboration.SesionCatalogo', on_delete=models.PROTECT, db_column='id_sesion', related_name='participante_sesion_catalogo_id_sesion_set')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, db_column='id_usuario', related_name='participante_sesion_catalogo_id_usuario_set')
    consentimiento = models.BooleanField(default=False)
    fecha_union = models.DateTimeField(blank=True, null=True)
    fecha_salida = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'participante_sesion_catalogo'
        constraints = [
            models.UniqueConstraint(fields=['sesion', 'usuario'], name="participante_sesion_catalogo_unique_0"),
        ]

    def __str__(self):
        return f"ParticipanteSesionCatalogo {self.pk}"


class EventoCatalogo(models.Model):
    id_evento_catalogo = models.BigAutoField(primary_key=True)
    sesion = models.ForeignKey('collaboration.SesionCatalogo', on_delete=models.PROTECT, db_column='id_sesion', related_name='evento_catalogo_id_sesion_set')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, db_column='id_usuario', related_name='evento_catalogo_id_usuario_set')
    producto = models.ForeignKey('catalog.Producto', on_delete=models.SET_NULL, db_column='id_producto', related_name='evento_catalogo_id_producto_set', blank=True, null=True)
    tipo_evento = models.CharField(max_length=32)
    fecha_evento = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'evento_catalogo'

    def __str__(self):
        return f"EventoCatalogo {self.pk}"


class Llamada(models.Model):
    id_llamada = models.BigAutoField(primary_key=True)
    conversacion = models.ForeignKey('messaging.Conversacion', on_delete=models.PROTECT, db_column='id_conversacion', related_name='llamada_id_conversacion_set')
    usuario_iniciador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, db_column='id_usuario_iniciador', related_name='llamada_id_usuario_iniciador_set')
    tipo = models.CharField(max_length=12)
    estado = models.CharField(max_length=24)
    fecha_invitacion = models.DateTimeField(default=timezone.now)
    fecha_inicio = models.DateTimeField(blank=True, null=True)
    fecha_fin = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'llamada'

    def __str__(self):
        return f"Llamada {self.pk}"


class ParticipanteLlamada(models.Model):
    id_participante_llamada = models.BigAutoField(primary_key=True)
    llamada = models.ForeignKey('collaboration.Llamada', on_delete=models.PROTECT, db_column='id_llamada', related_name='participante_llamada_id_llamada_set')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, db_column='id_usuario', related_name='participante_llamada_id_usuario_set')
    estado = models.CharField(max_length=24)
    fecha_union = models.DateTimeField(blank=True, null=True)
    fecha_salida = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'participante_llamada'
        constraints = [
            models.UniqueConstraint(fields=['llamada', 'usuario'], name="participante_llamada_unique_0"),
        ]

    def __str__(self):
        return f"ParticipanteLlamada {self.pk}"
