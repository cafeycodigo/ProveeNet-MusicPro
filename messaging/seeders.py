"""Datos de ejemplo del módulo messaging."""
from messaging.models import Conversacion, ParticipanteConversacion, Mensaje, ProductoCompartido, EventoConversacion
from core.seeding import ensure


def seed(context):
    users = context['users']
    buyer = context['buyer']
    seller = context['seller']
    comprador = context['comprador']
    proveedor = context['proveedor']
    producto = context['producto']
    conversacion = ensure(Conversacion, empresa_compradora=comprador,
                          empresa_proveedora=proveedor, producto_contexto=producto,
                          defaults={"estado": "abierta"})
    for user in users:
        ensure(ParticipanteConversacion, conversacion=conversacion, usuario=user)
    mensaje = ensure(Mensaje, conversacion=conversacion, usuario_remitente=buyer,
                     contenido="Necesitamos cotizar 10 osciloscopios X200.", defaults={
                         "empresa_remitente": comprador, "tipo": "texto",
                     })
    ensure(ProductoCompartido, conversacion=conversacion, mensaje=mensaje,
           producto=producto, usuario=buyer)
    ensure(EventoConversacion, conversacion=conversacion, tipo_evento="creada",
           defaults={"usuario": buyer, "datos": {"demo": True}})
    return {'conversacion': conversacion}
