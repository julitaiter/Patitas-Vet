from django.shortcuts import render
from django.views.generic import View, FormView
from .models import Consulta, Respuesta
from .forms import ConsultaForm

class ContactoView(FormView):
    template_name = 'contacto/contacto.html'
    form_class = ConsultaForm
    success_url = '/contacto/mensaje_enviado/'

    def form_valid(self, form):
        # Guardar la consulta en la base de datos
        form.save()
        form.send_mail()  # Enviar el correo electrónico con el mensaje de consulta

        return super().form_valid(form)
    
class MensajeEnviadoView(View):
    def get(self, request):
        return render(request, 'contacto/mensaje_enviado.html')
