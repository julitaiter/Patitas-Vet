from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('catalogo/', views.listar_catalogo, name='listar_catalogo'),
    path('catalogo/<str:model>/nuevo/', views.nuevo_item, name='nuevo_item'),
]