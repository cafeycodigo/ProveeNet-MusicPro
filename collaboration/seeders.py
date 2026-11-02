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
    from datetime import timedelta
    for index, (chat, buyer_user, seller_user, item) in enumerate(context["conversations"]):
        pending = index % 3 == 0
        start = now - timedelta(days=2, hours=1)
        end = start + timedelta(minutes=25)
        session = ensure(SesionCatalogo, conversacion=chat, usuario_iniciador=seller_user,
                         defaults={"producto_actual": item, "estado": "pendiente" if pending else "finalizada",
                                   "fecha_inicio": None if pending else start, "fecha_fin": None if pending else end})
        for user in (buyer_user, seller_user):
            ensure(ParticipanteSesionCatalogo, sesion=session, usuario=user, defaults={
                "consentimiento": not pending, "fecha_union": None if pending else start,
                "fecha_salida": None if pending else end})
        for event in (["invitacion"] if pending else ["invitacion", "aceptada", "producto_visto", "finalizada"]):
            ensure(EventoCatalogo, sesion=session, usuario=seller_user, tipo_evento=event,
                   defaults={"producto": item, "fecha_evento": start if event != "finalizada" else end})
        for kind in ("voz", "video"):
            call = ensure(Llamada, conversacion=chat, usuario_iniciador=seller_user, tipo=kind, defaults={
                "estado": "rechazada" if pending else "finalizada", "fecha_invitacion": start - timedelta(minutes=1),
                "fecha_inicio": None if pending else start, "fecha_fin": None if pending else end})
            for user in (buyer_user, seller_user):
                ensure(ParticipanteLlamada, llamada=call, usuario=user, defaults={
                    "estado": "rechazada" if pending else "finalizada", "fecha_union": None if pending else start,
                    "fecha_salida": None if pending else end})
    return {}
