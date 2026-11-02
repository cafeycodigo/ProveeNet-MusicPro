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
    from decimal import Decimal
    quotes = []
    orders = []
    for index in range(30 * context["scale"]):
        company = context["buyers"][index % len(context["buyers"]) ]
        author = context["teams"][company.pk][0]
        rfq = ensure(SolicitudCotizacion, empresa_compradora=company, titulo=f"DEMO-RFQ-{index + 1:04d} Equipamiento de estudio", defaults={
            "usuario_creador": author, "descripcion": "Solicitud multítem para ampliar estudio y salas de ensayo.",
            "estado": "cerrada" if index % 3 == 0 else "abierta", "fecha_solicitud": now - timedelta(days=5),
            "fecha_limite": now + timedelta(days=10)})
        request_items = [ensure(SolicitudDetalle, solicitud=rfq, descripcion_producto=f"Equipo de audio profesional tipo {line + 1}",
                               defaults={"cantidad": line + 2, "unidad_medida": "unidad"}) for line in range(3)]
        for supplier_index in range(3):
            supplier = context["suppliers"][(index + supplier_index) % len(context["suppliers"])]
            invitation = ensure(SolicitudProveedor, solicitud=rfq, empresa_proveedora=supplier, defaults={"estado": "respondida"})
            supplier_items = [p for p in context["products"] if p.empresa_id == supplier.pk][:3]
            for version in (1, 2):
                lines = [(detail, item, (item.precio_referencia * (Decimal("0.95") if version == 2 else 1)).quantize(Decimal("0.01")))
                         for detail, item in zip(request_items, supplier_items)]
                subtotal = sum((detail.cantidad * price for detail, _, price in lines), Decimal("0"))
                taxes = (subtotal * Decimal("0.19")).quantize(Decimal("0.01"))
                shipping = Decimal("75.00")
                accepted = index % 3 == 0 and supplier_index == 0 and version == 2
                state = "aceptada" if accepted else ("reemplazada" if version == 1 else "enviada")
                quote = ensure(Cotizacion, solicitud_proveedor=invitation, numero_version=version, defaults={
                    "moneda": "EUR", "subtotal": subtotal, "impuestos": taxes, "costo_envio": shipping,
                    "total": subtotal + taxes + shipping, "plazo_entrega_dias": 10 + supplier_index * 5,
                    "condiciones": "Pago 50% anticipado y saldo previo al despacho. Garantía de doce meses.",
                    "fecha_vencimiento": now + timedelta(days=15), "estado": state})
                for detail, item, price in lines:
                    ensure(CotizacionDetalle, cotizacion=quote, solicitud_detalle=detail, defaults={
                        "producto": item, "descripcion": item.nombre, "cantidad": detail.cantidad,
                        "precio_unitario": price, "subtotal": detail.cantidad * price})
                quotes.append((quote, author))
                if accepted:
                    orders.append(ensure(OrdenCompra, numero_orden=f"DEMO-MASS-OC-{index + 1:04d}", defaults={
                        "cotizacion": quote, "estado": "emitida", "total": quote.total, "moneda": quote.moneda}))
    context.update(quotes=quotes, orders=orders)
    return {'cotizacion': cotizacion}
