from django.contrib.auth.views import LoginView

from .forms import PortalAuthenticationForm


class PortalLoginView(LoginView):
    template_name = "app/portal/login.html"
    authentication_form = PortalAuthenticationForm
    redirect_authenticated_user = True
