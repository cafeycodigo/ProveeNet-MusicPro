"""Datos de ejemplo del módulo quotations."""
from datetime import timedelta
from django.utils import timezone
from quotations.models import SolicitudCotizacion, SolicitudDetalle, SolicitudProveedor, Cotizacion, CotizacionDetalle, OrdenCompra
from core.seeding import ensure


def seed(context):
    now = timezone.now()
    buyer = context['buyer']
    comprador = context['comprador']
    proveedor = context['proveedor']
    producto = context['producto']
    solicitud = ensure(SolicitudCotizacion, empresa_compradora=comprador,
                       titulo="Compra de 10 osciloscopios X200", defaults={
                           "usuario_creador": buyer, "estado": "cerrada",
                           "fecha_limite": now + timedelta(days=7),
                       })
    detalle = ensure(SolicitudDetalle, solicitud=solicitud, producto=producto, defaults={
        "descripcion_producto": producto.nombre, "cantidad": 10, "unidad_medida": "unidad",
    })
    invitacion = ensure(SolicitudProveedor, solicitud=solicitud,
                        empresa_proveedora=proveedor, defaults={"estado": "respondida"})
    cotizacion = ensure(Cotizacion, solicitud_proveedor=invitacion, numero_version=1,
                        defaults={"moneda": "EUR", "subtotal": 11000, "impuestos": 0,
                                  "costo_envio": 200, "total": 11200,
                                  "plazo_entrega_dias": 15, "estado": "aceptada"})
    ensure(CotizacionDetalle, cotizacion=cotizacion, solicitud_detalle=detalle,
           defaults={"producto": producto, "descripcion": producto.nombre,
                     "cantidad": 10, "precio_unitario": 1100, "subtotal": 11000})
    ensure(OrdenCompra, numero_orden="DEMO-OC-0001", defaults={
        "cotizacion": cotizacion, "estado": "emitida", "total": 11200, "moneda": "EUR",
    })
    return {'cotizacion': cotizacion}
