"""Datos de ejemplo del módulo companies."""
from companies.models import Pais, Empresa, UsuarioEmpresa
from core.seeding import ensure


def seed(context):
    buyer = context['buyer']
    seller = context['seller']
    chile = ensure(Pais, codigo_iso="CL", defaults={"nombre": "Chile"})
    alemania = ensure(Pais, codigo_iso="DE", defaults={"nombre": "Alemania"})
    comprador = ensure(Empresa, razon_social="Industrial Minera SpA", defaults={
        "pais": chile, "ciudad": "Santiago", "es_comprador": True,
        "es_proveedor": False, "verificada": True, "estado": "activa",
    })
    proveedor = ensure(Empresa, razon_social="TechIndustrial GmbH", defaults={
        "pais": alemania, "ciudad": "Berlín", "es_comprador": False,
        "es_proveedor": True, "verificada": True, "estado": "activa",
    })
    for user, empresa in [(buyer, comprador), (seller, proveedor)]:
        ensure(UsuarioEmpresa, usuario=user, empresa=empresa,
               defaults={"rol": "administrador", "activo": True})
    return {'chile': chile, 'alemania': alemania, 'comprador': comprador, 'proveedor': proveedor}
