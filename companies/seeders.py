"""Datos de ejemplo del módulo companies."""
from django.templatetags.static import static

from companies.models import Pais, Empresa, UsuarioEmpresa
from core.seeding import ensure


def seed(context):
    chile = ensure(Pais, codigo_iso="CL", defaults={"nombre": "Chile"})
    alemania = ensure(Pais, codigo_iso="DE", defaults={"nombre": "Alemania"})
    comprador = ensure(Empresa, razon_social="Industrial Minera SpA", defaults={
        "logo_url": static("companies/demo/industrial-minera.webp"),
        "pais": chile, "ciudad": "Santiago", "es_comprador": True,
        "es_proveedor": False, "verificada": True, "estado": "activa",
    })
    proveedor = ensure(Empresa, razon_social="TechIndustrial GmbH", defaults={
        "logo_url": static("companies/demo/techindustrial.webp"),
        "pais": alemania, "ciudad": "Berlín", "es_comprador": False,
        "es_proveedor": True, "verificada": True, "estado": "activa",
    })
    for empresa, asset in [(comprador, "industrial-minera"), (proveedor, "techindustrial")]:
        if not empresa.logo_url:
            empresa.logo_url = static(f"companies/demo/{asset}.webp")
            empresa.save(update_fields=["logo_url"])
    for index, user in enumerate(context["users"]):
        empresa = comprador if index % 2 == 0 else proveedor
        ensure(UsuarioEmpresa, usuario=user, empresa=empresa,
               defaults={"rol": "administrador", "activo": True})
    countries = []
    for code, name in [("CL", "Chile"), ("DE", "Alemania"), ("BR", "Brasil"), ("MX", "México"),
                       ("JP", "Japón"), ("IN", "India"), ("SN", "Senegal"), ("FR", "Francia"),
                       ("EG", "Egipto"), ("KR", "Corea del Sur")]:
        countries.append(ensure(Pais, codigo_iso=code, defaults={"nombre": name}))
    companies = [comprador, proveedor]
    names = ["Andes Audio", "Rhein Instruments", "Samba Sound", "Azteca Music", "Sakura Audio",
             "Mumbai Stage", "Dakar Sonido", "Paris Acoustics", "Nile Electronics", "Seoul Pro Audio"]
    for index in range(2, 20 * context["scale"]):
        supplier = index % 2 == 1
        companies.append(ensure(Empresa, razon_social=f"{names[index % 10]} Demo {index + 1:03d}", defaults={
            "nombre_comercial": f"{names[index % 10]} {index + 1:03d}", "pais": countries[index % 10],
            "identificacion_fiscal": f"DEMO-TAX-{index + 1:04d}", "ciudad": "Ciudad de demostración",
            "direccion": f"Avenida del Comercio {index + 100}",
            "descripcion": "Empresa ficticia dedicada a equipamiento musical y soluciones profesionales.",
            "sitio_web": f"https://empresa{index + 1}.example.com",
            "logo_url": static("companies/demo/techindustrial.webp" if supplier else "companies/demo/industrial-minera.webp"),
            "es_proveedor": supplier, "es_comprador": not supplier,
            "verificada": index % 4 != 0, "estado": "activa",
        }))
    teams = {company.pk: [] for company in companies}
    for index, user in enumerate(context["users"]):
        company = companies[index % len(companies)]
        role = "administrador" if not teams[company.pk] else "ejecutivo"
        ensure(UsuarioEmpresa, usuario=user, empresa=company, defaults={"rol": role, "activo": True})
        teams[company.pk].append(user)
    context.update(companies=companies, suppliers=companies[1::2], buyers=companies[::2], teams=teams)
    return {'chile': chile, 'alemania': alemania, 'comprador': comprador, 'proveedor': proveedor}
