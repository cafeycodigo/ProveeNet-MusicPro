"""Vistas para listar, agregar, editar y quitar miembros de una empresa."""

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from accounts.portal import get_portal_context
from notifications.models import Notificacion
from .models import Empresa, UsuarioEmpresa


def _contexto_equipo(request):
    """Prepara los datos comunes y verifica que el usuario administre una empresa."""
    contexto_portal = get_portal_context(request)

    if not contexto_portal.company or not contexto_portal.is_company_admin:
        raise PermissionDenied("Solo el administrador de la empresa puede gestionar su equipo.")

    if request.user.is_superuser:
        empresas_disponibles = Empresa.objects.filter(estado="activa").order_by("razon_social")
    else:
        empresas_disponibles = [
            membresia.empresa for membresia in contexto_portal.memberships
        ]

    if contexto_portal.mode == "supplier":
        url_busqueda = "app:dashboard_catalogo"
    else:
        url_busqueda = "app:dashboard_productos"

    return {
        "ctx": contexto_portal,
        "section": "equipo",
        "page_title": "Mi equipo",
        "navigation": contexto_portal.navigation,
        "company_options": empresas_disponibles,
        "search_url_name": url_busqueda,
        "unread_count": Notificacion.objects.filter(
            usuario=request.user,
            leida_en=None,
        ).count(),
    }


def _ultimo_administrador(miembro):
    """Evita dejar a una empresa sin un administrador activo."""
    es_administrador_activo = (
        miembro.rol == "administrador"
        and miembro.activo
        and miembro.usuario.is_active
    )
    if not es_administrador_activo:
        return False

    hay_otro_administrador = UsuarioEmpresa.objects.filter(
        empresa=miembro.empresa,
        rol="administrador",
        activo=True,
        usuario__is_active=True,
    ).exclude(pk=miembro.pk).exists()

    return not hay_otro_administrador


# READ: buscar los miembros y mostrarlos.
@login_required
@require_http_methods(["GET"])
def equipo(request):
    contexto = _contexto_equipo(request)

    miembros = (
        UsuarioEmpresa.objects
        .filter(empresa=contexto["ctx"].company)
        .select_related("usuario")
        .order_by("usuario__username")
    )
    busqueda = request.GET.get("q", "").strip()[:150]

    if busqueda:
        miembros = miembros.filter(
            Q(usuario__username__icontains=busqueda)
            | Q(usuario__first_name__icontains=busqueda)
            | Q(usuario__email__icontains=busqueda)
        )

    contexto.update(miembros=miembros, busqueda=busqueda)
    return render(request, "app/portal/equipo/listar.html", contexto)


# CREATE: validar los datos y agregar una membresía.
@login_required
@require_http_methods(["GET", "POST"])
def equipo_crear(request):
    contexto = _contexto_equipo(request)
    errores = []
    datos = {"identificador": "", "rol": "ejecutivo", "activo": True}

    if request.method == "POST":
        datos = {
            "identificador": request.POST.get("identificador", "").strip()[:254],
            "rol": request.POST.get("rol", ""),
            "activo": request.POST.get("activo") == "on",
        }

        # Se busca por nombre de usuario o correo, pero solo entre cuentas activas.
        if datos["identificador"]:
            usuarios = list(
                get_user_model().objects.filter(
                    Q(username__iexact=datos["identificador"])
                    | Q(email__iexact=datos["identificador"]),
                    is_active=True,
                )[:2]
            )
        else:
            usuarios = []

        # Dos resultados significan que el correo no identifica una cuenta única.
        if len(usuarios) != 1:
            errores.append(
                "Indica el usuario o correo de una cuenta activa. "
                "Si el correo se repite, usa el nombre de usuario."
            )

        roles_validos = ["administrador", "ejecutivo"]
        if datos["rol"] not in roles_validos:
            errores.append("Selecciona un rol válido: administrador o ejecutivo.")

        if not errores:
            try:
                with transaction.atomic():
                    UsuarioEmpresa.objects.create(
                        usuario=usuarios[0],
                        empresa=contexto["ctx"].company,
                        rol=datos["rol"],
                        activo=datos["activo"],
                    )
            except IntegrityError:
                errores.append("Esta cuenta ya pertenece al equipo. Puedes editar su membresía existente.")
            else:
                messages.success(request, "Miembro agregado al equipo.")
                return redirect("app:dashboard_equipo")
    contexto.update(datos=datos, errores=errores)
    return render(request, "app/portal/equipo/crear.html", contexto)


# UPDATE: buscar la membresía, validar los datos y guardar los cambios.
@login_required
@require_http_methods(["GET", "POST"])
def equipo_editar(request, miembro_id):
    contexto = _contexto_equipo(request)
    miembro = get_object_or_404(
        UsuarioEmpresa.objects.select_related("usuario"),
        pk=miembro_id,
        empresa=contexto["ctx"].company,
    )
    errores = []
    datos = {"rol": miembro.rol, "activo": miembro.activo}

    if request.method == "POST":
        datos = {
            "rol": request.POST.get("rol", ""),
            "activo": request.POST.get("activo") == "on",
        }
        roles_validos = ["administrador", "ejecutivo"]
        if datos["rol"] not in roles_validos:
            errores.append("Selecciona un rol válido: administrador o ejecutivo.")

        # El bloqueo evita cambios simultáneos que podrían dejar la empresa sin admin.
        with transaction.atomic():
            Empresa.objects.select_for_update().get(pk=miembro.empresa_id)
            miembro.refresh_from_db()
            quiere_quitar_admin = (
                datos["rol"] != "administrador" or not datos["activo"]
            )
            if quiere_quitar_admin and _ultimo_administrador(miembro):
                errores.append(
                    "No puedes desactivar ni cambiar el rol del último "
                    "administrador activo."
                )

            esta_editando_su_membresia = miembro.usuario_id == request.user.pk
            cambio_su_membresia = (
                datos["rol"] != miembro.rol or datos["activo"] != miembro.activo
            )
            if esta_editando_su_membresia and cambio_su_membresia:
                errores.append(
                    "No puedes cambiar tu propio rol o estado desde el equipo. "
                    "Solicítalo a otro administrador."
                )

            if not errores:
                miembro.rol = datos["rol"]
                miembro.activo = datos["activo"]
                miembro.save(update_fields=["rol", "activo"])
                messages.success(request, "Membresía actualizada.")
                return redirect("app:dashboard_equipo")
    contexto.update(miembro=miembro, datos=datos, errores=errores)
    return render(request, "app/portal/equipo/editar.html", contexto)


# DELETE: mostrar confirmación con GET y eliminar con POST.
@login_required
@require_http_methods(["GET", "POST"])
def equipo_eliminar(request, miembro_id):
    contexto = _contexto_equipo(request)
    miembro = get_object_or_404(
        UsuarioEmpresa.objects.select_related("usuario"),
        pk=miembro_id,
        empresa=contexto["ctx"].company,
    )
    errores = []

    if request.method == "POST":
        with transaction.atomic():
            # La membresía se vuelve a leer después de bloquear la empresa.
            Empresa.objects.select_for_update().get(pk=miembro.empresa_id)
            miembro.refresh_from_db()

            if miembro.usuario_id == request.user.pk:
                errores.append("No puedes quitar tu propia membresía desde el equipo.")

            if _ultimo_administrador(miembro):
                errores.append("No puedes quitar al último administrador activo de la empresa.")

            if not errores:
                miembro.delete()
                messages.success(request, "Miembro quitado del equipo. Su cuenta de usuario se conserva.")
                return redirect("app:dashboard_equipo")
    contexto.update(miembro=miembro, errores=errores)
    return render(request, "app/portal/equipo/eliminar.html", contexto)
