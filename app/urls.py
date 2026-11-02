from django.urls import path

from . import views
from . import dashboard
from companies import team_views
from catalog import views as catalog_views

app_name = "app"
urlpatterns = [
    path("", views.home, name="home"),
    path("home", dashboard.dashboard, name="dashboard"),
    path("home/", dashboard.dashboard),
    path("home/contexto", dashboard.switch_context, name="switch_context"),
    # Cada página tiene una URL, una vista y un nombre propios.
    path("home/explorar", dashboard.explorar, name="dashboard_explorar"),
    path("home/proveedores", dashboard.proveedores, name="dashboard_proveedores"),
    path("home/productos", dashboard.productos, name="dashboard_productos"),
    path("home/catalogo", dashboard.catalogo, name="dashboard_catalogo"),
    path("home/catalogo/nuevo", catalog_views.catalogo_crear, name="catalogo_crear"),
    path("home/catalogo/<int:producto_id>/editar", catalog_views.catalogo_editar, name="catalogo_editar"),
    path("home/catalogo/<int:producto_id>/eliminar", catalog_views.catalogo_eliminar, name="catalogo_eliminar"),
    path("home/ofertas", dashboard.ofertas, name="dashboard_ofertas"),
    path("home/favoritos", dashboard.favoritos, name="dashboard_favoritos"),
    path("home/mensajes", dashboard.mensajes, name="dashboard_mensajes"),
    path("home/cotizaciones", dashboard.cotizaciones, name="dashboard_cotizaciones"),
    path("home/reuniones", dashboard.reuniones, name="dashboard_reuniones"),
    path("home/pedidos", dashboard.pedidos, name="dashboard_pedidos"),
    path("home/empresa", dashboard.empresa, name="dashboard_empresa"),
    path("home/equipo", team_views.equipo, name="dashboard_equipo"),
    path("home/equipo/nuevo", team_views.equipo_crear, name="equipo_crear"),
    path("home/equipo/<int:miembro_id>/editar", team_views.equipo_editar, name="equipo_editar"),
    path("home/equipo/<int:miembro_id>/eliminar", team_views.equipo_eliminar, name="equipo_eliminar"),
    path("home/empresas", dashboard.empresas, name="dashboard_empresas"),
    path("home/usuarios", dashboard.usuarios, name="dashboard_usuarios"),
    path("home/categorias", dashboard.categorias, name="dashboard_categorias"),
    path("home/publicaciones", dashboard.publicaciones, name="dashboard_publicaciones"),
    path("home/notificaciones", dashboard.notificaciones, name="dashboard_notificaciones"),
    path("home/perfil", dashboard.perfil, name="dashboard_perfil"),
    path("app/presentacion", views.presentation, name="presentation"),
    path("app/presentacion/", views.presentation),
    path("app/presentacion/descargar", views.presentation_download, name="presentation_download"),
]
