"""Datos de ejemplo del módulo notifications."""
from notifications.models import Notificacion, HistorialEstado
from core.seeding import ensure


def seed(context):
    buyer = context['buyer']
    cotizacion = context['cotizacion']
    ensure(Notificacion, usuario=buyer, tipo="cotizacion", titulo="Cotización aceptada",
           defaults={"recurso_tipo": "cotizacion", "recurso_id": cotizacion.pk})
    ensure(HistorialEstado, entidad_tipo="cotizacion", entidad_id=cotizacion.pk,
           estado_nuevo="aceptada", defaults={"estado_anterior": "enviada", "usuario": buyer})
    from django.utils import timezone
    for index, user in enumerate(context["users"]):
        for number, kind in enumerate(["mensaje", "cotizacion", "oferta", "seguimiento", "catalogo"]):
            ensure(Notificacion, usuario=user, tipo=kind, titulo=f"Demo: actualización de {kind}", defaults={
                "contenido": "Hay novedades disponibles en tu red comercial de demostración.",
                "leida_en": timezone.now() if (index + number) % 2 == 0 else None})
    for quote, author in context["quotes"]:
        ensure(HistorialEstado, entidad_tipo="cotizacion", entidad_id=quote.pk, estado_nuevo=quote.estado,
               defaults={"estado_anterior": "borrador", "usuario": author,
                         "observacion": "Transición simulada del escenario comercial demo."})
    for order in context["orders"]:
        ensure(HistorialEstado, entidad_tipo="orden_compra", entidad_id=order.pk, estado_nuevo=order.estado,
               defaults={"observacion": "Orden emitida desde cotización aceptada."})
    return {}
