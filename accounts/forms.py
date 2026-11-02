from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


class PortalAuthenticationForm(AuthenticationForm):
    error_messages = {
        "invalid_login": "El usuario o la contraseña no son correctos. Revisa los datos e inténtalo nuevamente.",
        "inactive": "Esta cuenta está desactivada.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Usuario o correo electrónico"
        self.fields["username"].max_length = 254
        self.fields["username"].widget.attrs.update(
            autocomplete="username", placeholder="Tu usuario o correo", autofocus=True, maxlength=254,
        )
        self.fields["password"].label = "Contraseña"
        self.fields["password"].widget.attrs.update(
            autocomplete="current-password", placeholder="Tu contraseña",
        )

    def clean(self):
        identifier = self.cleaned_data.get("username", "").strip()
        if "@" in identifier:
            matches = list(get_user_model().objects.filter(email__iexact=identifier)[:2])
            if len(matches) > 1:
                raise ValidationError(self.error_messages["invalid_login"], code="invalid_login")
            if matches:
                self.cleaned_data["username"] = matches[0].get_username()
        return super().clean()
