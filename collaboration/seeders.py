"""Datos de ejemplo del módulo collaboration."""
from django.utils import timezone
from collaboration.models import SesionCatalogo, ParticipanteSesionCatalogo, EventoCatalogo, Llamada, ParticipanteLlamada
from core.seeding import ensure


def seed(context):
    now = timezone.now()
    users = context['users']
    seller = context['seller']
    producto = context['producto']
    conversacion = context['conversacion']
    sesion = ensure(SesionCatalogo, conversacion=conversacion, usuario_iniciador=seller,
                    defaults={"producto_actual": producto, "estado": "pendiente"})
    for user in users:
        ensure(ParticipanteSesionCatalogo, sesion=sesion, usuario=user)
    ensure(EventoCatalogo, sesion=sesion, usuario=seller, tipo_evento="invitacion",
           defaults={"producto": producto})
    llamada = ensure(Llamada, conversacion=conversacion, usuario_iniciador=seller,
                     tipo="video", defaults={"estado": "finalizada", "fecha_inicio": now,
                                             "fecha_fin": now})
    for user in users:
        ensure(ParticipanteLlamada, llamada=llamada, usuario=user,
               defaults={"estado": "finalizada"})
    return {}
