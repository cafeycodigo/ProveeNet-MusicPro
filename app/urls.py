from django.urls import path

from . import views
from . import dashboard

app_name = "app"
urlpatterns = [
    path("", views.home, name="home"),
    path("home", dashboard.dashboard, name="dashboard"),
    path("home/", dashboard.dashboard),
    path("home/contexto", dashboard.switch_context, name="switch_context"),
    path("home/<slug:section>", dashboard.dashboard, name="dashboard_section"),
    path("app/presentacion", views.presentation, name="presentation"),
    path("app/presentacion/", views.presentation),
    path("app/presentacion/descargar", views.presentation_download, name="presentation_download"),
]
