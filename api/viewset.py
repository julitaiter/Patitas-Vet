from rest_framework import viewsets
from .models import ServiciosApi
from .serializer import ServiciosApiSerializer

class ServiciosApiViewSet(viewsets.ModelViewSet):
    queryset = ServiciosApi.objects.all()
    serializer_class = ServiciosApiSerializer