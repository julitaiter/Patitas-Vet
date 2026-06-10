from django import forms
from django.forms import ModelForm
from .models import Consulta
from captcha.fields import CaptchaField

class ConsultaForm(ModelForm):
    captcha = CaptchaField()  # Agrega el campo de captcha al formulario

    class Meta:
        model = Consulta
        fields = ['nombre', 'email', 'mensaje', 'telefono']

    def send_mail(self):
        # Lógica para enviar el correo electrónico con el mensaje de consulta
        # Aquí puedes personalizar el contenido del correo electrónico y la dirección de destino
        subject = f"Consulta de {self.cleaned_data['nombre']}"
        message = f"Nombre: {self.cleaned_data['nombre']}\nEmail: {self.cleaned_data['email']}\nTeléfono: {self.cleaned_data['telefono']}\n\nMensaje:\n{self.cleaned_data['mensaje']}"
        recipient_list = ['admin@patitasvet.com']