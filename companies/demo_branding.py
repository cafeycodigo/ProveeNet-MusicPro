"""Identidades visuales compartidas por las variantes de cada empresa demo."""
from django.templatetags.static import static


COMPANY_BRANDS = [
    ("Andes Audio", "andes-audio"),
    ("Rhein Instruments", "rhein-instruments"),
    ("Samba Sound", "samba-sound"),
    ("Azteca Music", "azteca-music"),
    ("Sakura Audio", "sakura-audio"),
    ("Mumbai Stage", "mumbai-stage"),
    ("Dakar Sonido", "dakar-sonido"),
    ("Paris Acoustics", "paris-acoustics"),
    ("Nile Electronics", "nile-electronics"),
    ("Seoul Pro Audio", "seoul-pro-audio"),
]


def seed_brand_logo(company, asset):
    """Sustituye los dos logos compartidos anteriores y conserva logos propios."""
    old_urls = {static(f"companies/demo/{name}.webp")
                for name in ("industrial-minera", "techindustrial")}
    desired = static(f"companies/demo/{asset}.webp")
    if not company.logo_url or company.logo_url in old_urls:
        if company.logo_url != desired:
            company.logo_url = desired
            company.save(update_fields=["logo_url"])
    return company
