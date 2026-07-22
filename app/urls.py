from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),

    path("mi-perfil/", views.mi_perfil, name="mi_perfil"),
    path("mi-perfil/editar/", views.editar_perfil, name="editar_perfil"),

    path("catalogo/", views.listar_catalogo, name="listar_catalogo"),
    path("catalogo/nuevo/<str:model>/", views.nuevo_item, name="nuevo_item"),
    path("catalogo/<str:model>/<int:pk>/editar/", views.editar_item, name="editar_item"),
    path("catalogo/<str:model>/<int:pk>/eliminar/", views.eliminar_item, name="eliminar_item"),

    path("turnos/servicio/<int:servicio_pk>/nuevo/", views.solicitar_turno, name="solicitar_turno"),
    path("turnos/mis-turnos/", views.mis_turnos, name="mis_turnos"),
    path("turnos/horarios-disponibles/", views.horarios_disponibles, name="horarios_disponibles"),

    path("empleado/turnos/", views.gestionar_turnos, name="gestionar_turnos"),
    path("empleado/turnos/<int:pk>/editar/", views.editar_turno_empleado, name="editar_turno_empleado"),
    path("empleado/turnos/<int:pk>/estado/<str:estado>/", views.cambiar_estado_turno, name="cambiar_estado_turno"),
]