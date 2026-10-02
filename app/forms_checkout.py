from pathlib import Path

from django import forms

from .models import Pedido


class CheckoutForm(forms.Form):
    comprador_nombre = forms.CharField(max_length=100)
    comprador_apellido = forms.CharField(max_length=100)
    comprador_email = forms.EmailField()
    comprador_telefono = forms.CharField(max_length=40)
    comprador_dni = forms.CharField(max_length=20)
    tipo_factura = forms.ChoiceField(choices=Pedido.FACTURAS, initial="B")
    facturacion_mismos_datos = forms.BooleanField(required=False, initial=True)
    facturacion_nombre = forms.CharField(max_length=100, required=False)
    facturacion_apellido = forms.CharField(max_length=100, required=False)
    facturacion_dni = forms.CharField(max_length=20, required=False)
    facturacion_cuit = forms.CharField(max_length=20, required=False)
    facturacion_razon_social = forms.CharField(max_length=150, required=False)
    facturacion_domicilio = forms.CharField(max_length=255, required=False)
    facturacion_condicion_iva = forms.ChoiceField(choices=[("", "Elegir"), ("responsable_inscripto", "Responsable inscripto"), ("exento", "Exento")], required=False)
    facturacion_pais = forms.CharField(max_length=100, required=False)
    tipo_entrega = forms.ChoiceField(choices=Pedido.ENTREGAS)
    receptor_mismos_datos = forms.BooleanField(required=False, initial=True)
    receptor_nombre = forms.CharField(max_length=100, required=False)
    receptor_apellido = forms.CharField(max_length=100, required=False)
    receptor_dni = forms.CharField(max_length=20, required=False)
    receptor_telefono = forms.CharField(max_length=40, required=False)
    envio_calle = forms.CharField(max_length=120, required=False)
    envio_altura = forms.CharField(max_length=20, required=False)
    envio_piso_departamento = forms.CharField(max_length=60, required=False)
    envio_localidad = forms.CharField(max_length=100, required=False)
    envio_provincia = forms.CharField(max_length=100, required=False)
    envio_codigo_postal = forms.CharField(max_length=20, required=False)
    envio_referencias = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2}))
    medio_pago = forms.ChoiceField(choices=Pedido.PAGOS)
    comprobante = forms.FileField(required=False)
    cart_payload = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, configuracion=None, cuenta=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.configuracion = configuracion
        self.cuenta = cuenta
        labels = {
            "comprador_nombre": "Nombre", "comprador_apellido": "Apellido",
            "comprador_email": "Correo electrónico", "comprador_telefono": "Teléfono",
            "comprador_dni": "DNI", "tipo_factura": "Tipo de factura",
            "facturacion_mismos_datos": "Usar los mismos datos del comprador",
            "facturacion_nombre": "Nombre para la factura", "facturacion_apellido": "Apellido para la factura",
            "facturacion_dni": "DNI para la factura", "facturacion_cuit": "CUIT",
            "facturacion_razon_social": "Razón social", "facturacion_domicilio": "Domicilio de facturación",
            "facturacion_condicion_iva": "Condición frente al IVA", "facturacion_pais": "País de facturación",
            "tipo_entrega": "Forma de entrega", "receptor_mismos_datos": "Es la misma persona que realiza el pedido",
            "receptor_nombre": "Nombre de quien recibe o retira", "receptor_apellido": "Apellido de quien recibe o retira",
            "receptor_dni": "DNI de quien recibe o retira", "receptor_telefono": "Teléfono de quien recibe o retira",
            "envio_calle": "Calle", "envio_altura": "Altura / número",
            "envio_piso_departamento": "Piso y departamento (opcional)", "envio_localidad": "Localidad",
            "envio_provincia": "Provincia", "envio_codigo_postal": "Código postal",
            "envio_referencias": "Referencias para la entrega (opcional)", "medio_pago": "Medio de pago",
            "comprobante": "Comprobante de transferencia",
        }
        for nombre, label in labels.items():
            self.fields[nombre].label = label
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"
            elif isinstance(field.widget, forms.HiddenInput):
                continue
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs["class"] = "form-select"
            else:
                field.widget.attrs["class"] = "form-control"

    def clean_comprobante(self):
        archivo = self.cleaned_data.get("comprobante")
        if not archivo:
            return archivo
        extension = Path(archivo.name).suffix.lower()
        tipos = {".pdf": "application/pdf", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}
        if extension not in tipos:
            raise forms.ValidationError("El comprobante debe ser PDF, JPG o PNG.")
        if getattr(archivo, "content_type", tipos[extension]) not in (tipos[extension], "application/octet-stream"):
            raise forms.ValidationError("El tipo de archivo declarado no coincide con la extensión.")
        if archivo.size > (self.configuracion.comprobante_max_mb if self.configuracion else 10) * 1024 * 1024:
            raise forms.ValidationError("El comprobante supera el tamaño máximo permitido.")
        cabecera = archivo.read(8)
        archivo.seek(0)
        if not (cabecera.startswith(b"%PDF-") if extension == ".pdf" else cabecera.startswith(b"\xff\xd8\xff") if extension in (".jpg", ".jpeg") else cabecera.startswith(b"\x89PNG\r\n\x1a\n")):
            raise forms.ValidationError("El contenido del comprobante no coincide con su formato.")
        return archivo

    def clean(self):
        data = super().clean()
        factura = data.get("tipo_factura")
        if factura == "B" and not data.get("facturacion_mismos_datos"):
            self._requerir(data, "facturacion_nombre", "facturacion_apellido", "facturacion_dni", "facturacion_domicilio")
        if factura in ("A", "E"):
            data["facturacion_mismos_datos"] = False
            self._requerir(data, "facturacion_cuit", "facturacion_razon_social", "facturacion_domicilio", "facturacion_condicion_iva")
            if factura == "A":
                data["facturacion_pais"] = "Argentina"
            else:
                self._requerir(data, "facturacion_pais")
                if data.get("facturacion_pais", "").strip().casefold() == "argentina":
                    self.add_error("facturacion_pais", "Para Factura E el país debe ser distinto de Argentina.")
        if data.get("tipo_entrega") == "envio":
            self._requerir(data, "envio_calle", "envio_altura", "envio_localidad", "envio_provincia", "envio_codigo_postal")
        elif data.get("tipo_entrega") == "retiro" and not (self.configuracion and self.configuracion.nombre_tienda and self.configuracion.direccion_tienda):
            self.add_error("tipo_entrega", "El retiro no está disponible hasta configurar la tienda.")
        if not data.get("receptor_mismos_datos"):
            self._requerir(data, "receptor_nombre", "receptor_apellido", "receptor_dni", "receptor_telefono")
        if data.get("medio_pago") == "transferencia":
            if not self.cuenta:
                self.add_error("medio_pago", "La transferencia no está disponible.")
            if not data.get("comprobante"):
                self.add_error("comprobante", "Adjuntá el comprobante de transferencia.")
        return data

    def _requerir(self, data, *fields):
        for name in fields:
            if not data.get(name):
                self.add_error(name, "Este campo es obligatorio para la opción elegida.")
