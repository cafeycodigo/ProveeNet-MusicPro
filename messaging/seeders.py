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
    from datetime import timedelta
    from django.utils import timezone
    conversations = []
    scripts = ["Hola, buscamos equipamiento para un nuevo estudio.", "Gracias por contactarnos. ¿Qué cantidades necesitan?",
               "Necesitamos diez unidades con garantía y entrega internacional.", "Tenemos stock disponible y soporte técnico.",
               "¿Pueden enviarnos las especificaciones técnicas?", "Sí, este modelo incluye conexión digital y accesorios.",
               "Nos interesa comparar precios para nuestra próxima compra.", "Podemos preparar una cotización formal en EUR.",
               "Confirmen el plazo de entrega y las condiciones de pago.", "El plazo estimado es de quince días hábiles."]
    now = timezone.now()
    for index in range(40 * context["scale"]):
        company = context["buyers"][index % len(context["buyers"])]
        supplier = context["suppliers"][(index // len(context["buyers"])) % len(context["suppliers"])]
        item = next(p for p in context["products"] if p.empresa_id == supplier.pk)
        buyer_user = context["teams"][company.pk][0]
        seller_user = context["teams"][supplier.pk][0]
        chat = ensure(Conversacion, empresa_compradora=company, empresa_proveedora=supplier,
                      producto_contexto=item, defaults={"estado": "cerrada" if index % 5 == 0 else "abierta",
                                                       "fecha_creacion": now - timedelta(days=7)})
        for user in (buyer_user, seller_user):
            ensure(ParticipanteConversacion, conversacion=chat, usuario=user,
                   defaults={"ultima_lectura": now - timedelta(hours=1)})
        for number in range(20):
            user, sender = (buyer_user, company) if number % 2 == 0 else (seller_user, supplier)
            message = ensure(Mensaje, conversacion=chat, contenido=f"{number + 1:02d}. {scripts[number % 10]}",
                             usuario_remitente=user, defaults={"empresa_remitente": sender, "tipo": "texto",
                             "fecha_envio": now - timedelta(days=6, minutes=20 - number)})
            if number in (5, 15):
                ensure(ProductoCompartido, conversacion=chat, mensaje=message, producto=item, usuario=user)
        for event in ("creada", "producto_compartido"):
            ensure(EventoConversacion, conversacion=chat, tipo_evento=event,
                   defaults={"usuario": seller_user, "datos": {"demo": True, "producto_id": item.pk}})
        conversations.append((chat, buyer_user, seller_user, item))
    context["conversations"] = conversations
    return {'conversacion': conversacion}
