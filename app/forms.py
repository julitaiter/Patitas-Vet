from datetime import datetime

from django import forms
from django.contrib.auth import get_user_model
from django.forms import ModelForm

from .models import Producto, Servicio, Turno
from .services.turnos import obtener_horarios_disponibles, turno_esta_disponible


User = get_user_model()


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
        fields = ItemCatalogoForm.Meta.fields + ["sala", "duracion_minutos"]


class ProductoForm(ItemCatalogoForm):
    class Meta(ItemCatalogoForm.Meta):
        model = Producto
        fields = ItemCatalogoForm.Meta.fields + ["stock"]


class TurnoForm(forms.ModelForm):
    hora = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Hora",
    )

    class Meta:
        model = Turno
        fields = ["fecha", "hora", "mascota", "observaciones"]
        widgets = {
            "fecha": forms.DateInput(
                attrs={"class": "form-control", "type": "date"},
                format="%Y-%m-%d",
            ),
            "mascota": forms.TextInput(attrs={"class": "form-control"}),
            "observaciones": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        self.servicio = kwargs.pop("servicio", None)

        super().__init__(*args, **kwargs)

        self.fields["fecha"].input_formats = ["%Y-%m-%d"]
        self.fields["hora"].choices = [("", "Seleccioná una fecha")]

        fecha_str = self.data.get("fecha") if self.data else None

        if self.servicio and fecha_str:
            try:
                fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
                horarios = obtener_horarios_disponibles(
                    self.servicio.sala, fecha)

                if horarios:
                    self.fields["hora"].choices = [
                        (hora.strftime("%H:%M"), hora.strftime("%H:%M"))
                        for hora in horarios
                    ]
                else:
                    self.fields["hora"].choices = [
                        ("", "No hay horarios disponibles")]
            except ValueError:
                pass

    def clean_hora(self):
        hora = self.cleaned_data.get("hora")

        if not hora:
            raise forms.ValidationError("Seleccioná un horario.")

        return datetime.strptime(hora, "%H:%M").time()

    def clean(self):
        cleaned_data = super().clean()

        fecha = cleaned_data.get("fecha")
        hora = cleaned_data.get("hora")

        if self.servicio and fecha and hora:
            if not turno_esta_disponible(self.servicio.sala, fecha, hora):
                raise forms.ValidationError(
                    "El horario seleccionado no está disponible."
                )

        return cleaned_data


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

    def clean(self):
        cleaned_data = super().clean()

        servicio = cleaned_data.get("servicio")
        fecha = cleaned_data.get("fecha")
        hora = cleaned_data.get("hora")

        if servicio and fecha and hora:
            qs = Turno.objects.filter(
                sala=servicio.sala,
                fecha=fecha,
                hora=hora,
            ).exclude(estado=Turno.ESTADO_CANCELADO)

            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise forms.ValidationError(
                    "Ya existe un turno para la sala de este servicio en esa fecha y horario."
                )

        return cleaned_data
