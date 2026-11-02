"""Modelos del módulo quotations."""
from django.db import models
from django.db.models import F, Q
from django.utils import timezone


class SolicitudCotizacion(models.Model):
    id_solicitud = models.BigAutoField(primary_key=True)
    empresa_compradora = models.ForeignKey('companies.Empresa', on_delete=models.PROTECT, db_column='id_empresa_compradora', related_name='solicitud_cotizacion_id_empresa_compradora_set')
    usuario_creador = models.ForeignKey('accounts.Usuario', on_delete=models.PROTECT, db_column='id_usuario_creador', related_name='solicitud_cotizacion_id_usuario_creador_set')
    titulo = models.CharField(max_length=180)
    descripcion = models.TextField(blank=True, null=True)
    fecha_solicitud = models.DateTimeField(default=timezone.now)
    fecha_limite = models.DateTimeField(blank=True, null=True)
    estado = models.CharField(max_length=24)

    class Meta:
        db_table = 'solicitud_cotizacion'

    def __str__(self):
        return self.titulo or "SolicitudCotizacion"


class SolicitudDetalle(models.Model):
    id_detalle = models.BigAutoField(primary_key=True)
    solicitud = models.ForeignKey('quotations.SolicitudCotizacion', on_delete=models.PROTECT, db_column='id_solicitud', related_name='solicitud_detalle_id_solicitud_set')
    producto = models.ForeignKey('catalog.Producto', on_delete=models.SET_NULL, db_column='id_producto', related_name='solicitud_detalle_id_producto_set', blank=True, null=True)
    descripcion_producto = models.TextField()
    cantidad = models.DecimalField(max_digits=18, decimal_places=3)
    unidad_medida = models.CharField(max_length=32)

    class Meta:
        db_table = 'solicitud_detalle'
        constraints = [
            models.CheckConstraint(condition=Q(cantidad__gt=0), name="solicitud_detalle_cantidad_valid"),
        ]

    def __str__(self):
        return f"SolicitudDetalle {self.pk}"


class SolicitudProveedor(models.Model):
    id_solicitud_proveedor = models.BigAutoField(primary_key=True)
    solicitud = models.ForeignKey('quotations.SolicitudCotizacion', on_delete=models.PROTECT, db_column='id_solicitud', related_name='solicitud_proveedor_id_solicitud_set')
    empresa_proveedora = models.ForeignKey('companies.Empresa', on_delete=models.PROTECT, db_column='id_empresa_proveedora', related_name='solicitud_proveedor_id_empresa_proveedora_set')
    fecha_invitacion = models.DateTimeField(default=timezone.now)
    estado = models.CharField(max_length=24)

    class Meta:
        db_table = 'solicitud_proveedor'
        constraints = [
            models.UniqueConstraint(fields=['solicitud', 'empresa_proveedora'], name="solicitud_proveedor_unique_0"),
        ]

    def __str__(self):
        return f"SolicitudProveedor {self.pk}"


class Cotizacion(models.Model):
    id_cotizacion = models.BigAutoField(primary_key=True)
    solicitud_proveedor = models.ForeignKey('quotations.SolicitudProveedor', on_delete=models.PROTECT, db_column='id_solicitud_proveedor', related_name='cotizacion_id_solicitud_proveedor_set')
    numero_version = models.IntegerField()
    moneda = models.CharField(max_length=3)
    subtotal = models.DecimalField(max_digits=18, decimal_places=2)
    impuestos = models.DecimalField(max_digits=18, decimal_places=2)
    costo_envio = models.DecimalField(max_digits=18, decimal_places=2)
    total = models.DecimalField(max_digits=18, decimal_places=2)
    plazo_entrega_dias = models.IntegerField(blank=True, null=True)
    condiciones = models.TextField(blank=True, null=True)
    archivo_pdf_url = models.TextField(blank=True, null=True)
    fecha_emision = models.DateTimeField(default=timezone.now)
    fecha_vencimiento = models.DateTimeField(blank=True, null=True)
    estado = models.CharField(max_length=24)

    class Meta:
        db_table = 'cotizacion'
        constraints = [
            models.UniqueConstraint(fields=['solicitud_proveedor', 'numero_version'], name="cotizacion_unique_0"),
            models.CheckConstraint(condition=Q(numero_version__gt=0), name="cotizacion_numero_version_valid"),
            models.CheckConstraint(condition=Q(subtotal__gte=0), name="cotizacion_subtotal_valid"),
            models.CheckConstraint(condition=Q(impuestos__gte=0), name="cotizacion_impuestos_valid"),
            models.CheckConstraint(condition=Q(costo_envio__gte=0), name="cotizacion_costo_envio_valid"),
            models.CheckConstraint(condition=Q(total__gte=0), name="cotizacion_total_valid"),
            models.CheckConstraint(condition=Q(plazo_entrega_dias__gte=0), name="cotizacion_plazo_entrega_dias_valid"),
        ]

    def __str__(self):
        return f"Cotizacion {self.pk}"


class CotizacionDetalle(models.Model):
    id_cotizacion_detalle = models.BigAutoField(primary_key=True)
    cotizacion = models.ForeignKey('quotations.Cotizacion', on_delete=models.PROTECT, db_column='id_cotizacion', related_name='cotizacion_detalle_id_cotizacion_set')
    solicitud_detalle = models.ForeignKey('quotations.SolicitudDetalle', on_delete=models.SET_NULL, db_column='id_solicitud_detalle', related_name='cotizacion_detalle_id_solicitud_detalle_set', blank=True, null=True)
    producto = models.ForeignKey('catalog.Producto', on_delete=models.SET_NULL, db_column='id_producto', related_name='cotizacion_detalle_id_producto_set', blank=True, null=True)
    descripcion = models.TextField()
    cantidad = models.DecimalField(max_digits=18, decimal_places=3)
    precio_unitario = models.DecimalField(max_digits=18, decimal_places=2)
    subtotal = models.DecimalField(max_digits=18, decimal_places=2)

    class Meta:
        db_table = 'cotizacion_detalle'
        constraints = [
            models.CheckConstraint(condition=Q(cantidad__gt=0), name="cotizacion_detalle_cantidad_valid"),
            models.CheckConstraint(condition=Q(precio_unitario__gte=0), name="cotizacion_detalle_precio_unitario_valid"),
            models.CheckConstraint(condition=Q(subtotal__gte=0), name="cotizacion_detalle_subtotal_valid"),
        ]

    def __str__(self):
        return f"CotizacionDetalle {self.pk}"


class OrdenCompra(models.Model):
    id_orden = models.BigAutoField(primary_key=True)
    cotizacion = models.OneToOneField('quotations.Cotizacion', on_delete=models.PROTECT, db_column='id_cotizacion', related_name='orden_compra_id_cotizacion_set')
    numero_orden = models.CharField(max_length=60, unique=True)
    fecha_emision = models.DateTimeField(default=timezone.now)
    estado = models.CharField(max_length=24)
    total = models.DecimalField(max_digits=18, decimal_places=2)
    moneda = models.CharField(max_length=3)

    class Meta:
        db_table = 'orden_compra'
        constraints = [
            models.CheckConstraint(condition=Q(total__gte=0), name="orden_compra_total_valid"),
        ]

    def __str__(self):
        return self.numero_orden or "OrdenCompra"
