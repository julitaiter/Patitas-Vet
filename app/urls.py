from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("catalogo/", views.listar_catalogo, name="listar_catalogo"),
    path("catalogo/nuevo/<str:model>/", views.nuevo_item, name="nuevo_item"),
    path("catalogo/<str:model>/<int:pk>/editar/", views.editar_item, name="editar_item"),
    path("catalogo/<str:model>/<int:pk>/eliminar/", views.eliminar_item, name="eliminar_item"),
    path("turnos/servicio/<int:servicio_pk>/nuevo/", views.solicitar_turno, name="solicitar_turno"),
    path("turnos/mis-turnos/", views.mis_turnos, name="mis_turnos"),
]