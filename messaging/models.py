from django.conf import settings
"""Modelos del módulo messaging."""
from django.db import models
from django.db.models import F, Q
from django.utils import timezone


class Conversacion(models.Model):
    id_conversacion = models.BigAutoField(primary_key=True)
    empresa_compradora = models.ForeignKey('companies.Empresa', on_delete=models.PROTECT, db_column='id_empresa_compradora', related_name='conversacion_id_empresa_compradora_set')
    empresa_proveedora = models.ForeignKey('companies.Empresa', on_delete=models.PROTECT, db_column='id_empresa_proveedora', related_name='conversacion_id_empresa_proveedora_set')
    producto_contexto = models.ForeignKey('catalog.Producto', on_delete=models.SET_NULL, db_column='id_producto_contexto', related_name='conversacion_id_producto_contexto_set', blank=True, null=True)
    estado = models.CharField(max_length=24)
    fecha_creacion = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'conversacion'
        constraints = [
            models.CheckConstraint(condition=~Q(empresa_compradora=F("empresa_proveedora")), name="conversacion_empresas_distintas"),
        ]

    def __str__(self):
        return f"Conversacion {self.pk}"


class ParticipanteConversacion(models.Model):
    id_participante = models.BigAutoField(primary_key=True)
    conversacion = models.ForeignKey('messaging.Conversacion', on_delete=models.PROTECT, db_column='id_conversacion', related_name='participante_conversacion_id_conversacion_set')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, db_column='id_usuario', related_name='participante_conversacion_id_usuario_set')
    ultima_lectura = models.DateTimeField(blank=True, null=True)
    fecha_ingreso = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'participante_conversacion'
        constraints = [
            models.UniqueConstraint(fields=['conversacion', 'usuario'], name="participante_conversacion_unique_0"),
        ]

    def __str__(self):
        return f"ParticipanteConversacion {self.pk}"


class Mensaje(models.Model):
    id_mensaje = models.BigAutoField(primary_key=True)
    conversacion = models.ForeignKey('messaging.Conversacion', on_delete=models.PROTECT, db_column='id_conversacion', related_name='mensaje_id_conversacion_set')
    usuario_remitente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, db_column='id_usuario_remitente', related_name='mensaje_id_usuario_remitente_set')
    empresa_remitente = models.ForeignKey('companies.Empresa', on_delete=models.PROTECT, db_column='id_empresa_remitente', related_name='mensaje_id_empresa_remitente_set')
    tipo = models.CharField(max_length=24)
    contenido = models.TextField(blank=True, null=True)
    archivo_url = models.TextField(blank=True, null=True)
    fecha_envio = models.DateTimeField(default=timezone.now)
    fecha_edicion = models.DateTimeField(blank=True, null=True)
    eliminado_en = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'mensaje'

    def __str__(self):
        return f"Mensaje {self.pk}"


class ProductoCompartido(models.Model):
    id_producto_compartido = models.BigAutoField(primary_key=True)
    conversacion = models.ForeignKey('messaging.Conversacion', on_delete=models.PROTECT, db_column='id_conversacion', related_name='producto_compartido_id_conversacion_set')
    mensaje = models.ForeignKey('messaging.Mensaje', on_delete=models.SET_NULL, db_column='id_mensaje', related_name='producto_compartido_id_mensaje_set', blank=True, null=True)
    producto = models.ForeignKey('catalog.Producto', on_delete=models.PROTECT, db_column='id_producto', related_name='producto_compartido_id_producto_set')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, db_column='id_usuario', related_name='producto_compartido_id_usuario_set')
    fecha_compartido = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'producto_compartido'

    def __str__(self):
        return f"ProductoCompartido {self.pk}"


class EventoConversacion(models.Model):
    id_evento = models.BigAutoField(primary_key=True)
    conversacion = models.ForeignKey('messaging.Conversacion', on_delete=models.PROTECT, db_column='id_conversacion', related_name='evento_conversacion_id_conversacion_set')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, db_column='id_usuario', related_name='evento_conversacion_id_usuario_set', blank=True, null=True)
    tipo_evento = models.CharField(max_length=40)
    datos = models.JSONField(default=dict, blank=True, null=True)
    fecha_evento = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'evento_conversacion'

    def __str__(self):
        return f"EventoConversacion {self.pk}"
