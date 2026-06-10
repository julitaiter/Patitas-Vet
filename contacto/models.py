from django.db import models
from django.utils.html import format_html

# Create your models here.
class Consulta(models.Model):
    CONTESTADA = 'contestada'
    NO_CONTESTADA = 'no_contestada'
    EN_PROCESO = 'en_proceso'
    ESTADO_CHOICES = [
        (CONTESTADA, 'Contestada'),
        (NO_CONTESTADA, 'No contestada'),
        (EN_PROCESO, 'En proceso'),
    ]

    nombre = models.CharField(max_length=40)
    email = models.EmailField()
    mensaje = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=EN_PROCESO)
    fecha = models.DateTimeField(auto_now_add=True)
    telefono = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.nombre
    
    def estado_respuesta(self):
        if self.estado == self.CONTESTADA:
            return format_html("<span style='color: green;'>{}</span>", "Contestada")
        elif self.estado == self.NO_CONTESTADA:
            return format_html("<span style='color: orange;'>{}</span>", "No contestada")
        elif self.estado == self.EN_PROCESO:
            return format_html("<span style='color: red;'>{}</span>", "En proceso")
        
class Respuesta(models.Model):
    consulta = models.ForeignKey(Consulta, on_delete=models.CASCADE, related_name='respuestas')
    mensaje = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Respuesta a {self.consulta.nombre} - {self.fecha.strftime('%Y-%m-%d %H:%M:%S')}"
    
    def create_mensaje(self):
        self.consulta.estado = self.consulta.CONTESTADA
        self.consulta.save()

        # LÓGICA DE ENVÍO DE MENSAJE (SIMULADA)

        return f"Hola {self.consulta.nombre},\n\nGracias por contactarnos. Hemos recibido tu consulta y nos pondremos en contacto contigo lo antes posible.\n\nMensaje original:\n{self.consulta.mensaje}\n\nSaludos,\nEquipo de Patitas Vet"
    
    def save(self, *args, **kwargs):
        self.create_mensaje()
        force_update = False
        if self.pk is not None:
            force_update = True
        super(Respuesta, self).save(force_update=force_update, *args, **kwargs)