from django.contrib.auth.views import LoginView
from django.conf import settings
from django.contrib.auth import get_user_model

from .forms import PortalAuthenticationForm


class PortalLoginView(LoginView):
    template_name = "app/portal/login.html"
    authentication_form = PortalAuthenticationForm
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["demo_accounts"] = []
        if not settings.DEBUG or not getattr(settings, "DEMO_LOGIN_ENABLED", False):
            return context
        password = settings.DEMO_LOGIN_PASSWORD
        profiles = [
            ("demo_admin", "Administrador de plataforma", "Supervisa empresas, usuarios y catálogo.", "users"),
            ("demo_comprador", "Comprador / administrador de empresa", "Explora proveedores y revisa las compras de tu empresa.", "company"),
            ("demo_proveedor", "Proveedor / administrador de empresa", "Consulta tu catálogo y las solicitudes recibidas.", "box"),
            ("demo_individual", "Comprador individual", "Explora la red con una cuenta personal.", "user"),
        ]
        users = {u.username: u for u in get_user_model().objects.filter(
            username__in=[p[0] for p in profiles], is_active=True)}
        for username, title, description, icon in profiles:
            user = users.get(username)
            # Nunca publica claves de cuentas normales ni credenciales que ya no sean válidas.
            if user and user.check_password(password):
                context["demo_accounts"].append({
                    "username": username, "email": user.email if user.email and
                    get_user_model().objects.filter(email__iexact=user.email).count() == 1 else "",
                    "title": title, "description": description, "icon": icon,
                    "password": password,
                })
        return context
