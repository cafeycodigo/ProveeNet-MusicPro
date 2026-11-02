from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import PortalLoginView

app_name = "accounts"
urlpatterns = [
    path("login", PortalLoginView.as_view(), name="login"),
    path("login/", PortalLoginView.as_view()),
    path("logout", LogoutView.as_view(), name="logout"),
]
