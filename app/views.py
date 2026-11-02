import json
from pathlib import Path

from django.conf import settings
from django.db.models import Count, Prefetch, Q
from django.http import FileResponse, Http404
from django.shortcuts import render

from catalog.models import Categoria, Producto
from companies.models import Empresa, Pais


def presentation(request):
    slides = json.loads((Path(__file__).with_name("presentation_data.json")).read_text(encoding="utf-8"))
    return render(request, "app/presentation.html", {"slides": slides})


def presentation_download(request):
    path = settings.BASE_DIR / "entregables" / "ProveeNet-presentacion.pptx"
    if not path.is_file():
        raise Http404("La presentación todavía no está disponible.")
    return FileResponse(path.open("rb"), as_attachment=True, filename=path.name)


def home(request):
    """Directorio público de proveedores activos con filtros combinables."""
    query = request.GET.get("q", "").strip()[:180]
    country = request.GET.get("pais", "").strip()[:2].upper()
    category = request.GET.get("categoria", "").strip()[:150]
    origin = request.GET.get("origen", "CL").strip()[:2].upper()
    if not Pais.objects.filter(codigo_iso=origin).exists():
        origin = ""
    scope = request.GET.get("alcance", "global")
    if scope not in {"global", "local", "internacional"} or not origin:
        scope = "global"
    suppliers = Empresa.objects.filter(es_proveedor=True, estado="activa").annotate(
        product_count=Count("producto_id_empresa_set", filter=Q(
            producto_id_empresa_set__activo=True), distinct=True),
    )
    if query:
        suppliers = suppliers.filter(
            Q(razon_social__icontains=query)
            | Q(nombre_comercial__icontains=query)
            | Q(descripcion__icontains=query)
            | Q(producto_id_empresa_set__nombre__icontains=query,
                producto_id_empresa_set__activo=True)
        )
    if country:
        suppliers = suppliers.filter(pais__codigo_iso=country)
    if scope == "local":
        suppliers = suppliers.filter(pais__codigo_iso=origin)
    elif scope == "internacional":
        suppliers = suppliers.exclude(pais__codigo_iso=origin)
    if category:
        suppliers = suppliers.filter(
            producto_id_empresa_set__categoria__slug=category,
            producto_id_empresa_set__categoria__activa=True,
            producto_id_empresa_set__activo=True,
        )
    suppliers = suppliers.select_related("pais").prefetch_related(Prefetch(
        "producto_id_empresa_set", queryset=Producto.objects.filter(activo=True)
        .select_related("categoria").order_by("nombre"), to_attr="public_products",
    )).distinct().order_by("-verificada", "razon_social")
    return render(request, "app/home.html", {
        "suppliers": suppliers[:24],
        "result_count": suppliers.count(),
        "countries": Pais.objects.filter(
            empresa_id_pais_set__es_proveedor=True,
            empresa_id_pais_set__estado="activa",
        ).distinct().order_by("nombre"),
        "categories": Categoria.objects.filter(activa=True).order_by("nombre"),
        "query": query, "country": country, "category": category,
        "origin": origin, "scope": scope,
        "origin_countries": Pais.objects.order_by("nombre"),
        "network_countries": Pais.objects.filter(
            empresa_id_pais_set__es_proveedor=True,
            empresa_id_pais_set__estado="activa",
        ).distinct().count(),
        "network_suppliers": Empresa.objects.filter(es_proveedor=True, estado="activa").count(),
        "has_filters": bool(query or country or category or scope != "global"),
    })
