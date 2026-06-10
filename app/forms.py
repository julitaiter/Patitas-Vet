from django import forms
from django.forms import ModelForm

from .models import Servicio, Producto, Turno


class BootstrapFormMixin:
    def aplicar_clases_bootstrap(self):
        for field in self.fields.values():
            widget = field.widget

            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(widget, forms.Select):
                widget.attrs.setdefault("class", "form-select")
            else:
                widget.attrs.setdefault("class", "form-control")


class ItemCatalogoForm(BootstrapFormMixin, ModelForm):
    class Meta:
        fields = [
            "nombre",
            "descripcion",
            "precio",
            "imagen",
            "categoria",
            "activo",
            "destacado",
        ]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 4}),
            "precio": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aplicar_clases_bootstrap()


class ServicioForm(ItemCatalogoForm):
    class Meta(ItemCatalogoForm.Meta):
        model = Servicio
        fields = ItemCatalogoForm.Meta.fields + ["duracion_minutos"]


class ProductoForm(ItemCatalogoForm):
    class Meta(ItemCatalogoForm.Meta):
        model = Producto
        fields = ItemCatalogoForm.Meta.fields + ["stock"]


class TurnoForm(BootstrapFormMixin, ModelForm):
    class Meta:
        model = Turno
        fields = ["fecha", "hora", "mascota", "observaciones"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}),
            "hora": forms.TimeInput(attrs={"type": "time"}),
            "observaciones": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aplicar_clases_bootstrap()
