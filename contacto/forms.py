from django import forms
from django.forms import ModelForm
from .models import Consulta
from captcha.fields import CaptchaField
from app.forms import BootstrapFormMixin

class ConsultaForm(BootstrapFormMixin,  ModelForm):
    captcha = CaptchaField()  # Agrega el campo de captcha al formulario

    class Meta:
        model = Consulta
        fields = ['nombre', 'email', 'mensaje', 'telefono']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and getattr(user, 'is_authenticated', False):
            nombre_usuario = user.get_full_name() or getattr(user, 'username', '')
            email_usuario = getattr(user, 'email', '')
            if nombre_usuario:
                self.initial.setdefault('nombre', nombre_usuario)
            if email_usuario:
                self.initial.setdefault('email', email_usuario)
        self.aplicar_clases_bootstrap()

    def send_mail(self):
        # Lógica para enviar el correo electrónico con el mensaje de consulta
        # Aquí puedes personalizar el contenido del correo electrónico y la dirección de destino
        subject = f"Consulta de {self.cleaned_data['nombre']}"
        message = f"Nombre: {self.cleaned_data['nombre']}\nEmail: {self.cleaned_data['email']}\nTeléfono: {self.cleaned_data['telefono']}\n\nMensaje:\n{self.cleaned_data['mensaje']}"
        recipient_list = ['admin@patitasvet.com']