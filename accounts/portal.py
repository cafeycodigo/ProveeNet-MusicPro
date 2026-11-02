"""Contexto empresarial y navegación. El rol nunca proviene de un parámetro público."""
from dataclasses import dataclass

from companies.models import Empresa, UsuarioEmpresa


MENU = {
    "inicio": ("Inicio", "home"), "explorar": ("Explorar", "search"),
    "proveedores": ("Proveedores", "company"), "productos": ("Productos", "box"),
    "catalogo": ("Mi catálogo", "box"), "ofertas": ("Ofertas", "tag"),
    "favoritos": ("Mis favoritos", "heart"), "mensajes": ("Mensajes", "chat"),
    "cotizaciones": ("Cotizaciones", "file"), "reuniones": ("Reuniones", "calendar"),
    "pedidos": ("Pedidos", "order"), "empresa": ("Mi empresa", "company"),
    "equipo": ("Mi equipo", "users"), "empresas": ("Empresas", "company"),
    "usuarios": ("Usuarios", "users"), "categorias": ("Categorías", "box"),
    "publicaciones": ("Publicaciones", "file"), "notificaciones": ("Notificaciones", "bell"),
    "perfil": ("Mi perfil", "user"),
}


@dataclass
class PortalContext:
    company: object
    membership: object
    mode: str
    is_company_admin: bool
    memberships: list

    @property
    def platform(self):
        return self.mode == "platform"

    @property
    def label(self):
        return {"platform": "Administrador de plataforma", "buyer": "Comprador",
                "supplier": "Proveedor", "individual": "Comprador individual",
                "company": "Miembro de empresa"}[self.mode]

    @property
    def navigation(self):
        if self.platform:
            keys = ["inicio", "empresas", "usuarios", "productos", "categorias",
                    "cotizaciones", "publicaciones", "notificaciones"]
        elif self.mode == "individual":
            keys = ["inicio", "explorar", "proveedores", "favoritos", "notificaciones", "perfil"]
        else:
            keys = ["inicio"]
            if self.mode == "buyer":
                keys += ["explorar", "proveedores", "productos", "ofertas", "favoritos"]
            elif self.mode == "supplier":
                keys += ["catalogo", "ofertas"]
            keys += ["mensajes", "cotizaciones", "reuniones", "pedidos", "empresa"]
            if self.is_company_admin:
                keys += ["equipo"]
            keys += ["notificaciones", "perfil"]
        return [{"key": key, "label": MENU[key][0], "icon": MENU[key][1]} for key in keys]


def get_portal_context(request):
    memberships = list(UsuarioEmpresa.objects.filter(
        usuario=request.user, activo=True, empresa__estado="activa",
    ).select_related("empresa", "empresa__pais").order_by("pk"))
    selected = request.session.get("portal_company")
    membership = next((item for item in memberships if str(item.empresa_id) == str(selected)), None)
    company = None
    if request.user.is_superuser:
        if selected:
            company = Empresa.objects.select_related("pais").filter(pk=selected, estado="activa").first()
        if company is None:
            return PortalContext(None, None, "platform", False, memberships)
    else:
        membership = membership or (memberships[0] if memberships else None)
        company = membership.empresa if membership else None
    if company is None:
        return PortalContext(None, None, "individual", False, memberships)
    modes = []
    if company.es_comprador:
        modes.append("buyer")
    if company.es_proveedor:
        modes.append("supplier")
    mode = request.session.get("portal_mode")
    if mode not in modes:
        mode = modes[0] if modes else "company"
    return PortalContext(company, membership, mode,
                         request.user.is_superuser or membership.rol == "administrador", memberships)
