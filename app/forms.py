from .models import Turno
from django import forms
from django.forms import ModelForm

from .models import Servicio, Producto, Turno

from django import forms
from django.contrib.auth import get_user_model


User = get_user_model()


class PerfilForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name"]
        labels = {
            "username": "Usuario",
            "first_name": "Nombre",
            "last_name": "Apellido",
        }
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
        }


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


class TurnoForm(forms.ModelForm):
    class Meta:
        model = Turno
        fields = ["fecha", "hora", "mascota", "observaciones"]
        widgets = {
            "fecha": forms.DateInput(
                attrs={"class": "form-control", "type": "date"},
                format="%Y-%m-%d",
            ),
            "hora": forms.TimeInput(
                attrs={"class": "form-control", "type": "time"},
                format="%H:%M",
            ),
            "mascota": forms.TextInput(attrs={"class": "form-control"}),
            "observaciones": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["fecha"].input_formats = ["%Y-%m-%d"]
        self.fields["hora"].input_formats = ["%H:%M"]
        self.aplicar_clases_bootstrap()


class TurnoEmpleadoForm(forms.ModelForm):
    class Meta:
        model = Turno
        fields = ["servicio", "fecha", "hora",
                  "mascota", "observaciones", "estado"]
        widgets = {
            "servicio": forms.Select(attrs={"class": "form-select"}),
            "fecha": forms.DateInput(
                attrs={"class": "form-control", "type": "date"},
                format="%Y-%m-%d",
            ),
            "hora": forms.TimeInput(
                attrs={"class": "form-control", "type": "time"},
                format="%H:%M",
            ),
            "mascota": forms.TextInput(attrs={"class": "form-control"}),
            "observaciones": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "estado": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["fecha"].input_formats = ["%Y-%m-%d"]
        self.fields["hora"].input_formats = ["%H:%M"]
