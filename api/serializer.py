from .models import ServiciosApi
from rest_framework import serializers

class ServiciosApiSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiciosApi
        fields = '__all__'