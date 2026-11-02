from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from accounts.portal import get_portal_context
from companies.models import Empresa
from notifications.models import Notificacion

from .forms import ProductoForm
from .models import Producto


def _contexto_catalogo(request):
    """Prepara el encabezado del panel y comprueba el espacio de proveedor."""
    ctx = get_portal_context(request)
    if not ctx.company or ctx.mode != "supplier":
        raise PermissionDenied("El catálogo solo está disponible en el espacio de proveedor.")

    if request.user.is_superuser:
        empresas = Empresa.objects.filter(estado="activa").order_by("razon_social")
    else:
        empresas = [membresia.empresa for membresia in ctx.memberships]

    return {
        "ctx": ctx,
        "section": "catalogo",
        "page_title": "Mi catálogo",
        "navigation": ctx.navigation,
        "company_options": empresas,
        "search_url_name": "app:dashboard_catalogo",
        "unread_count": Notificacion.objects.filter(
            usuario=request.user,
            leida_en=None,
        ).count(),
    }


def _producto_de_mi_empresa(request, producto_id):
    """Busca un producto solo dentro de la empresa activa."""
    contexto = _contexto_catalogo(request)
    producto = get_object_or_404(
        Producto,
        pk=producto_id,
        empresa=contexto["ctx"].company,
    )
    return contexto, producto


@login_required
@require_http_methods(["GET", "POST"])
def catalogo_crear(request):
    """Muestra el formulario y guarda un producto nuevo."""
    contexto = _contexto_catalogo(request)
    producto = Producto(empresa=contexto["ctx"].company)
    formulario = ProductoForm(request.POST or None, instance=producto)

    if request.method == "POST" and formulario.is_valid():
        formulario.save()
        messages.success(request, "Producto agregado al catálogo.")
        return redirect("app:dashboard_catalogo")

    contexto.update(
        formulario=formulario,
        titulo="Agregar producto",
        texto_boton="Guardar producto",
    )
    return render(request, "app/portal/catalogo/formulario.html", contexto)


@login_required
@require_http_methods(["GET", "POST"])
def catalogo_editar(request, producto_id):
    """Muestra el producto existente y guarda los cambios enviados."""
    contexto, producto = _producto_de_mi_empresa(request, producto_id)
    formulario = ProductoForm(request.POST or None, instance=producto)

    if request.method == "POST" and formulario.is_valid():
        formulario.save()
        messages.success(request, "Producto actualizado.")
        return redirect("app:dashboard_catalogo")

    contexto.update(
        formulario=formulario,
        titulo="Editar producto",
        texto_boton="Guardar cambios",
    )
    return render(request, "app/portal/catalogo/formulario.html", contexto)


@login_required
@require_http_methods(["GET", "POST"])
def catalogo_eliminar(request, producto_id):
    """Pide confirmación y elimina el producto si no tiene datos relacionados."""
    contexto, producto = _producto_de_mi_empresa(request, producto_id)

    if request.method == "POST":
        try:
            producto.delete()
        except ProtectedError:
            messages.error(
                request,
                "No se puede eliminar este producto porque tiene información relacionada. "
                "Puedes dejarlo inactivo desde el formulario de edición.",
            )
        else:
            messages.success(request, "Producto eliminado del catálogo.")
        return redirect("app:dashboard_catalogo")

    contexto["producto"] = producto
    return render(request, "app/portal/catalogo/eliminar.html", contexto)
