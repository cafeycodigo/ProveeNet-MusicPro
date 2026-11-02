"""Modelos del módulo catalog."""
from django.db import models
from django.db.models import F, Q
from django.utils import timezone


class Categoria(models.Model):
    id_categoria = models.BigAutoField(primary_key=True)
    categoria_padre = models.ForeignKey('catalog.Categoria', on_delete=models.SET_NULL, db_column='id_categoria_padre', related_name='categoria_id_categoria_padre_set', blank=True, null=True)
    nombre = models.CharField(max_length=120)
    slug = models.CharField(max_length=150, unique=True)
    activa = models.BooleanField(default=True)

    class Meta:
        db_table = 'categoria'

    def __str__(self):
        return self.nombre or "Categoria"


class Producto(models.Model):
    id_producto = models.BigAutoField(primary_key=True)
    empresa = models.ForeignKey('companies.Empresa', on_delete=models.PROTECT, db_column='id_empresa', related_name='producto_id_empresa_set')
    categoria = models.ForeignKey('catalog.Categoria', on_delete=models.PROTECT, db_column='id_categoria', related_name='producto_id_categoria_set')
    nombre = models.CharField(max_length=180)
    sku = models.CharField(max_length=80)
    marca = models.CharField(max_length=120, blank=True, null=True)
    modelo = models.CharField(max_length=120, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    precio_referencia = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    moneda = models.CharField(max_length=3, blank=True, null=True)
    stock = models.IntegerField(blank=True, null=True)
    requiere_cotizacion = models.BooleanField(default=True)
    activo = models.BooleanField(default=True)
    fecha_publicacion = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'producto'
        constraints = [
            models.UniqueConstraint(fields=['empresa', 'sku'], name="producto_unique_0"),
            models.CheckConstraint(condition=Q(stock__gte=0), name="producto_stock_valid"),
            models.CheckConstraint(condition=Q(precio_referencia__gte=0), name="producto_precio_referencia_valid"),
            models.CheckConstraint(condition=(Q(precio_referencia__isnull=True, moneda__isnull=True) | (Q(precio_referencia__isnull=False, moneda__isnull=False) & ~Q(moneda=""))), name="producto_precio_moneda"),
        ]

    def __str__(self):
        return self.nombre or "Producto"


class ProductoImagen(models.Model):
    id_imagen = models.BigAutoField(primary_key=True)
    producto = models.ForeignKey('catalog.Producto', on_delete=models.PROTECT, db_column='id_producto', related_name='producto_imagen_id_producto_set')
    archivo_url = models.TextField()
    texto_alternativo = models.CharField(max_length=255, blank=True, null=True)
    orden = models.IntegerField()
    es_portada = models.BooleanField(default=False)

    class Meta:
        db_table = 'producto_imagen'

    def __str__(self):
        return f"ProductoImagen {self.pk}"


class Oferta(models.Model):
    id_oferta = models.BigAutoField(primary_key=True)
    producto = models.ForeignKey('catalog.Producto', on_delete=models.PROTECT, db_column='id_producto', related_name='oferta_id_producto_set')
    titulo = models.CharField(max_length=180)
    precio_oferta = models.DecimalField(max_digits=18, decimal_places=2)
    moneda = models.CharField(max_length=3)
    fecha_inicio = models.DateTimeField(default=timezone.now)
    fecha_fin = models.DateTimeField(default=timezone.now)
    activa = models.BooleanField(default=True)

    class Meta:
        db_table = 'oferta'
        constraints = [
            models.CheckConstraint(condition=Q(precio_oferta__gte=0), name="oferta_precio_oferta_valid"),
            models.CheckConstraint(condition=Q(fecha_fin__gt=F("fecha_inicio")), name="oferta_fechas_validas"),
        ]

    def __str__(self):
        return self.titulo or "Oferta"
