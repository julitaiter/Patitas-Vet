from django import forms
from django.forms import ModelForm
from .models import ItemCatalogo, Producto, Servicio

class ItemCatalogoForm(ModelForm):
    class Meta:
        model = ItemCatalogo
        fields = ['nombre', 'descripcion', 'precio', 'imagen', 'categoria']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ServicioForm(ItemCatalogoForm):
    class Meta(ItemCatalogoForm.Meta):
        model = Servicio

class ProductoForm(ItemCatalogoForm):
    class Meta(ItemCatalogoForm.Meta):
        model = Producto