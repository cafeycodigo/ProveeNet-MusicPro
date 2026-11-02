from django.contrib.auth.forms import AuthenticationForm


class PortalAuthenticationForm(AuthenticationForm):
    error_messages = {
        "invalid_login": "El usuario o la contraseña no son correctos. Revisa los datos e inténtalo nuevamente.",
        "inactive": "Esta cuenta está desactivada.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Nombre de usuario"
        self.fields["username"].widget.attrs.update(
            autocomplete="username", placeholder="Tu nombre de usuario", autofocus=True,
        )
        self.fields["password"].label = "Contraseña"
        self.fields["password"].widget.attrs.update(
            autocomplete="current-password", placeholder="Tu contraseña",
        )
