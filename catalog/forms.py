from django import forms

from .models import Categoria, Producto


class ProductoForm(forms.ModelForm):
    """Formulario para crear y editar productos del catálogo de una empresa."""

    class Meta:
        model = Producto
        fields = [
            "nombre",
            "sku",
            "categoria",
            "marca",
            "modelo",
            "descripcion",
            "precio_referencia",
            "moneda",
            "stock",
            "requiere_cotizacion",
            "activo",
        ]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 4}),
            "precio_referencia": forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
            "stock": forms.NumberInput(attrs={"min": "0", "step": "1"}),
        }
        labels = {
            "nombre": "Nombre del producto",
            "sku": "Código (SKU)",
            "categoria": "Categoría",
            "marca": "Marca",
            "modelo": "Modelo",
            "descripcion": "Descripción",
            "precio_referencia": "Precio de referencia",
            "moneda": "Moneda (por ejemplo, CLP o USD)",
            "stock": "Unidades disponibles",
            "requiere_cotizacion": "El comprador debe solicitar una cotización",
            "activo": "Producto activo",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        categorias = Categoria.objects.filter(activa=True)
        if self.instance.pk:
            categorias = Categoria.objects.filter(
                pk=self.instance.categoria_id,
            ) | categorias
        self.fields["categoria"].queryset = categorias.distinct().order_by("nombre")

        self.fields["marca"].required = False
        self.fields["modelo"].required = False
        self.fields["descripcion"].required = False
        self.fields["precio_referencia"].required = False
        self.fields["moneda"].required = False
        self.fields["stock"].required = False

    def clean(self):
        datos = super().clean()
        precio = datos.get("precio_referencia")
        moneda = datos.get("moneda")

        if precio is None and moneda:
            self.add_error("moneda", "Indica un precio o deja la moneda vacía.")
        elif precio is not None and not moneda:
            self.add_error("moneda", "Indica la moneda del precio.")

        sku = datos.get("sku")
        empresa = self.instance.empresa
        if sku and empresa:
            sku_ya_usado = Producto.objects.filter(
                empresa=empresa,
                sku=sku,
            ).exclude(pk=self.instance.pk).exists()
            if sku_ya_usado:
                self.add_error("sku", "Tu empresa ya usa ese código para otro producto.")

        return datos
