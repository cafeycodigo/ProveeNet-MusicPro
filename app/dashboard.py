"""Panel privado. Todas las consultas comerciales usan la empresa activa autorizada."""
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.portal import MENU, SECTION_URL_NAMES, get_portal_context
from catalog.models import Categoria, Oferta, Producto
from collaboration.models import Llamada
from companies.models import Empresa, UsuarioEmpresa
from messaging.models import Conversacion
from notifications.models import Notificacion
from quotations.models import Cotizacion, OrdenCompra, SolicitudCotizacion, SolicitudProveedor
from social.models import Favorito, Publicacion, SeguimientoProveedor


def scoped_data(request, ctx):
    """Una sola política para tarjetas, tablas y listados de cada perfil."""
    products = Producto.objects.select_related("empresa", "categoria")
    quotes = Cotizacion.objects.select_related("solicitud_proveedor__solicitud", "solicitud_proveedor__empresa_proveedora")
    orders = OrdenCompra.objects.select_related("cotizacion__solicitud_proveedor__solicitud")
    requests = SolicitudCotizacion.objects.all()
    invitations = SolicitudProveedor.objects.select_related("solicitud", "solicitud__empresa_compradora")
    conversations = Conversacion.objects.select_related("empresa_compradora", "empresa_proveedora")
    if not ctx.platform:
        products = products.filter(empresa=ctx.company) if ctx.mode == "supplier" else products.filter(
            activo=True, empresa__estado="activa", empresa__es_proveedor=True)
        if ctx.company:
            company = ctx.company
            if ctx.mode == "supplier":
                quotes = quotes.filter(solicitud_proveedor__empresa_proveedora=company)
                orders = orders.filter(cotizacion__solicitud_proveedor__empresa_proveedora=company)
            else:
                quotes = quotes.filter(solicitud_proveedor__solicitud__empresa_compradora=company)
                orders = orders.filter(cotizacion__solicitud_proveedor__solicitud__empresa_compradora=company)
            requests = requests.filter(empresa_compradora=company)
            invitations = invitations.filter(empresa_proveedora=company)
            conversations = conversations.filter(Q(empresa_compradora=company) | Q(empresa_proveedora=company))
            if not ctx.is_company_admin:
                conversations = conversations.filter(participante_conversacion_id_conversacion_set__usuario=request.user)
        else:
            quotes, orders, requests, invitations, conversations = (
                quotes.none(), orders.none(), requests.none(), invitations.none(), conversations.none())
    meetings = Llamada.objects.filter(conversacion__in=conversations)
    if not ctx.platform and not ctx.is_company_admin:
        meetings = meetings.filter(participante_llamada_id_llamada_set__usuario=request.user)
    return {
        "products": products, "quotes": quotes, "orders": orders, "requests": requests,
        "invitations": invitations, "conversations": conversations.distinct(), "meetings": meetings.distinct(),
        "favorites": Favorito.objects.filter(usuario=request.user).select_related("producto__empresa"),
        "notifications": Notificacion.objects.filter(usuario=request.user),
    }


def money(amount, currency):
    return f"{amount:,.2f} {currency}" if amount is not None else "Por cotizar"


def section_table(request, ctx, data, section):
    """Listados de consulta; las operaciones se incorporan en sus módulos correspondientes."""
    q = request.GET.get("q", "").strip()[:180]
    rows, headers = [], []
    if section in {"productos", "catalogo", "explorar"}:
        # data["products"] ya está limitado al espacio al que tiene acceso el usuario.
        qs = data["products"]
        if q:
            qs = qs.filter(
                Q(nombre__icontains=q)
                | Q(empresa__razon_social__icontains=q)
                | Q(sku__icontains=q)
            )
        headers = ["Producto", "Empresa", "Categoría", "Referencia", "Estado"]
        if section == "catalogo":
            headers.append("Acciones")

        for producto in qs.order_by("-pk")[:100]:
            precio = money(producto.precio_referencia, producto.moneda)
            estado = "Activo" if producto.activo else "Inactivo"
            fila = [
                producto.nombre,
                producto.empresa.razon_social,
                producto.categoria.nombre,
                precio,
                estado,
            ]
            if section == "catalogo":
                fila.append(producto.pk)
            rows.append(fila)
    elif section in {"empresas", "proveedores"}:
        qs = Empresa.objects.select_related("pais")
        if not ctx.platform:
            qs = qs.filter(es_proveedor=True, estado="activa")
        if q:
            qs = qs.filter(Q(razon_social__icontains=q) | Q(pais__nombre__icontains=q))
        headers = ["Empresa", "País", "Tipo", "Verificación", "Estado"]
        rows = [[c.razon_social, c.pais.nombre, "Compradora y proveedora" if c.es_comprador and c.es_proveedor else
                 "Proveedora" if c.es_proveedor else "Compradora", "Verificada" if c.verificada else "Pendiente", c.estado]
                for c in qs.order_by("razon_social")[:100]]
    elif section == "usuarios":
        headers = ["Usuario", "Nombre", "Correo", "Acceso", "Estado"]
        qs = get_user_model().objects.all()
        if q:
            qs = qs.filter(Q(username__icontains=q) | Q(first_name__icontains=q))
        rows = [[u.username, u.get_full_name() or "Sin nombre", u.email or "Sin correo",
                 "Plataforma" if u.is_superuser else "Personal de administración" if u.is_staff else "Usuario",
                 "Activo" if u.is_active else "Inactivo"] for u in qs.order_by("username")[:100]]
    elif section == "cotizaciones":
        headers = ["Solicitud", "Proveedor", "Versión", "Total", "Estado"]
        qs = data["quotes"]
        if q:
            qs = qs.filter(solicitud_proveedor__solicitud__titulo__icontains=q)
        rows = [[c.solicitud_proveedor.solicitud.titulo, c.solicitud_proveedor.empresa_proveedora.razon_social,
                 c.numero_version, money(c.total, c.moneda), c.estado] for c in qs.order_by("-fecha_emision")[:100]]
    elif section == "pedidos":
        headers = ["Orden", "Solicitud", "Total", "Emisión", "Estado"]
        qs = data["orders"]
        if q:
            qs = qs.filter(numero_orden__icontains=q)
        rows = [[o.numero_orden, o.cotizacion.solicitud_proveedor.solicitud.titulo,
                 money(o.total, o.moneda), o.fecha_emision.strftime("%d/%m/%Y"), o.estado]
                for o in qs.order_by("-fecha_emision")[:100]]
    elif section == "mensajes":
        headers = ["Conversación", "Empresa compradora", "Empresa proveedora", "Inicio", "Estado"]
        qs = data["conversations"]
        if q:
            qs = qs.filter(Q(empresa_compradora__razon_social__icontains=q) | Q(empresa_proveedora__razon_social__icontains=q))
        rows = [[f"Conversación #{c.pk}", c.empresa_compradora.razon_social, c.empresa_proveedora.razon_social,
                 c.fecha_creacion.strftime("%d/%m/%Y"), c.estado] for c in qs.order_by("-fecha_creacion")[:100]]
    elif section == "reuniones":
        headers = ["Reunión", "Tipo", "Invitación", "Estado"]
        rows = [[f"Reunión #{m.pk}", m.tipo, m.fecha_invitacion.strftime("%d/%m/%Y"), m.estado]
                for m in data["meetings"].order_by("-fecha_invitacion")[:100]]
    elif section == "ofertas":
        qs = Oferta.objects.select_related("producto__empresa")
        if ctx.mode == "supplier":
            qs = qs.filter(producto__empresa=ctx.company)
        else:
            qs = qs.filter(activa=True, producto__activo=True, producto__empresa__estado="activa",
                           fecha_inicio__lte=timezone.now(), fecha_fin__gte=timezone.now())
        if q:
            qs = qs.filter(titulo__icontains=q)
        headers = ["Oferta", "Producto", "Precio", "Vigencia", "Estado"]
        rows = [[o.titulo, o.producto.nombre, money(o.precio_oferta, o.moneda),
                 o.fecha_fin.strftime("%d/%m/%Y"), "Activa" if o.activa else "Inactiva"] for o in qs[:100]]
    elif section == "favoritos":
        headers = ["Producto", "Proveedor", "Guardado"]
        rows = [[f.producto.nombre, f.producto.empresa.razon_social, f.fecha_creacion.strftime("%d/%m/%Y")]
                for f in data["favorites"].order_by("-fecha_creacion")[:100]]
    elif section == "notificaciones":
        headers = ["Notificación", "Descripción", "Fecha", "Estado"]
        rows = [[n.titulo, n.contenido or "Sin descripción", n.fecha_creacion.strftime("%d/%m/%Y"),
                 "Leída" if n.leida_en else "Sin leer"] for n in data["notifications"].order_by("-fecha_creacion")[:100]]
    elif section == "categorias":
        headers = ["Categoría", "Identificador", "Estado"]
        qs = Categoria.objects.all()
        if q:
            qs = qs.filter(nombre__icontains=q)
        rows = [[c.nombre, c.slug, "Activa" if c.activa else "Inactiva"] for c in qs.order_by("nombre")[:100]]
    elif section == "publicaciones":
        headers = ["Publicación", "Empresa", "Visibilidad", "Estado"]
        qs = Publicacion.objects.select_related("empresa")
        if q:
            qs = qs.filter(titulo__icontains=q)
        rows = [[p.titulo or "Sin título", p.empresa.razon_social, p.visibilidad, p.estado] for p in qs[:100]]
    return headers, rows


def _render_dashboard(request, section):
    """Preparación compartida de datos. Las vistas públicas están definidas abajo."""
    ctx = get_portal_context(request)
    allowed = {item["key"] for item in ctx.navigation}
    if section not in allowed:
        raise PermissionDenied("Tu perfil no tiene acceso a esta sección.")
    data = scoped_data(request, ctx)
    if ctx.platform:
        metrics = [("Empresas registradas", Empresa.objects.count(), "company", "empresas"),
                   ("Usuarios activos", get_user_model().objects.filter(is_active=True).count(), "users", "usuarios"),
                   ("Productos", data["products"].count(), "box", "productos"),
                   ("Empresas por verificar", Empresa.objects.filter(verificada=False).count(), "check", "empresas")]
        overview_section = "empresas"
        greeting = "Tu plataforma, de un vistazo"
    elif ctx.mode == "supplier":
        metrics = [("Productos de mi empresa", data["products"].count(), "box", "catalogo"),
                   ("Solicitudes recibidas", data["invitations"].count(), "file", "cotizaciones"),
                   ("Cotizaciones enviadas", data["quotes"].count(), "file", "cotizaciones"),
                   ("Órdenes de compra", data["orders"].count(), "order", "pedidos")]
        overview_section, greeting = "cotizaciones", "Todo listo para conectar con tus clientes"
    elif ctx.company:
        metrics = [("Solicitudes de mi empresa", data["requests"].count(), "file", "cotizaciones"),
                   ("Cotizaciones recibidas", data["quotes"].count(), "file", "cotizaciones"),
                   ("Órdenes de compra", data["orders"].count(), "order", "pedidos"),
                   ("Mis favoritos", data["favorites"].count(), "heart", "favoritos")]
        overview_section, greeting = "cotizaciones", "Tu próxima conexión comienza aquí"
    else:
        metrics = [("Proveedores disponibles", Empresa.objects.filter(es_proveedor=True, estado="activa").count(), "company", "proveedores"),
                   ("Mis favoritos", data["favorites"].count(), "heart", "favoritos"),
                   ("Proveedores que sigo", SeguimientoProveedor.objects.filter(usuario=request.user).count(), "users", "proveedores"),
                   ("Avisos sin leer", data["notifications"].filter(leida_en=None).count(), "bell", "notificaciones")]
        overview_section, greeting = "favoritos", "Encuentra nuevas posibilidades para tus compras"
    headers, rows = section_table(request, ctx, data, overview_section if section == "inicio" else section)
    if section == "inicio":
        rows = rows[:5]
    company_options = Empresa.objects.filter(estado="activa").order_by("razon_social") if request.user.is_superuser else [m.empresa for m in ctx.memberships]
    return render(request, "app/portal/dashboard.html", {
        "ctx": ctx, "navigation": ctx.navigation, "section": section, "page_title": MENU[section][0],
        "greeting": greeting, "metrics": [{"label": label, "value": value, "icon": icon, "section": target, "url_name": SECTION_URL_NAMES[target]}
                                          for label, value, icon, target in metrics if target in allowed],
        "table_headers": headers, "table_rows": rows,
        "table_title": MENU[overview_section][0] if section == "inicio" else MENU[section][0],
        "overview_section": overview_section, "overview_url_name": SECTION_URL_NAMES[overview_section],
        "page_url_name": SECTION_URL_NAMES[section], "query": request.GET.get("q", "")[:180],
        "search_url_name": SECTION_URL_NAMES["catalogo" if ctx.mode == "supplier" else "explorar" if ctx.mode == "individual" else "productos"],
        "searchable": section in {"empresas", "proveedores", "productos", "catalogo", "explorar", "usuarios", "equipo", "cotizaciones", "pedidos", "mensajes", "ofertas", "categorias", "publicaciones"},
        "company_options": company_options,
        "notifications": data["notifications"].order_by("-fecha_creacion")[:4],
        "unread_count": data["notifications"].filter(leida_en=None).count(),
        "featured_products": data["products"].filter(activo=True).order_by("-pk")[:3],
        "invitations": data["invitations"].order_by("-fecha_invitacion")[:4] if ctx.mode == "supplier" else [],
    })


@login_required
@require_POST
def switch_context(request):
    value = request.POST.get("company", "")
    if not value and request.user.is_superuser:
        request.session.pop("portal_company", None)
        request.session.pop("portal_mode", None)
        return redirect("app:dashboard")
    if not value.isdecimal():
        raise PermissionDenied
    company = Empresa.objects.filter(pk=value, estado="activa").first()
    if not company or (not request.user.is_superuser and not UsuarioEmpresa.objects.filter(
            usuario=request.user, empresa=company, activo=True).exists()):
        raise PermissionDenied("No tienes acceso a esa empresa.")
    mode = request.POST.get("mode", "buyer")
    allowed_modes = (["buyer"] if company.es_comprador else []) + (["supplier"] if company.es_proveedor else [])
    if mode not in allowed_modes:
        mode = allowed_modes[0] if allowed_modes else "company"
    request.session["portal_company"] = company.pk
    request.session["portal_mode"] = mode
    return redirect("app:dashboard")


# Vistas de cada página: permite seguir urls.py y encontrar su función directamente.
@login_required
def dashboard(request):
    """Inicio del espacio de trabajo según el perfil del usuario."""
    return _render_dashboard(request, "inicio")


@login_required
def explorar(request):
    """Página de explorar del espacio de trabajo."""
    return _render_dashboard(request, "explorar")


@login_required
def proveedores(request):
    """Página de proveedores del espacio de trabajo."""
    return _render_dashboard(request, "proveedores")


@login_required
def productos(request):
    """Página de productos del espacio de trabajo."""
    return _render_dashboard(request, "productos")


@login_required
def catalogo(request):
    """Muestra el catálogo del proveedor dentro del espacio de trabajo.

    _render_dashboard prepara la empresa autorizada y encuentra sus productos.
    La plantilla del panel muestra el resultado en una tabla.
    """
    return _render_dashboard(request, "catalogo")


@login_required
def ofertas(request):
    """Página de ofertas del espacio de trabajo."""
    return _render_dashboard(request, "ofertas")


@login_required
def favoritos(request):
    """Página de favoritos del espacio de trabajo."""
    return _render_dashboard(request, "favoritos")


@login_required
def mensajes(request):
    """Página de mensajes del espacio de trabajo."""
    return _render_dashboard(request, "mensajes")


@login_required
def cotizaciones(request):
    """Página de cotizaciones del espacio de trabajo."""
    return _render_dashboard(request, "cotizaciones")


@login_required
def reuniones(request):
    """Página de reuniones del espacio de trabajo."""
    return _render_dashboard(request, "reuniones")


@login_required
def pedidos(request):
    """Página de pedidos del espacio de trabajo."""
    return _render_dashboard(request, "pedidos")


@login_required
def empresa(request):
    """Página de empresa del espacio de trabajo."""
    return _render_dashboard(request, "empresa")


@login_required
def empresas(request):
    """Página de empresas del espacio de trabajo."""
    return _render_dashboard(request, "empresas")


@login_required
def usuarios(request):
    """Página de usuarios del espacio de trabajo."""
    return _render_dashboard(request, "usuarios")


@login_required
def categorias(request):
    """Página de categorias del espacio de trabajo."""
    return _render_dashboard(request, "categorias")


@login_required
def publicaciones(request):
    """Página de publicaciones del espacio de trabajo."""
    return _render_dashboard(request, "publicaciones")


@login_required
def notificaciones(request):
    """Página de notificaciones del espacio de trabajo."""
    return _render_dashboard(request, "notificaciones")


@login_required
def perfil(request):
    """Página de perfil del espacio de trabajo."""
    return _render_dashboard(request, "perfil")
