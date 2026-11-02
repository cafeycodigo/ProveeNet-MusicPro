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
    return {}
