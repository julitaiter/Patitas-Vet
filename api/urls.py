from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.routers import SimpleRouter

from api.views import (
    BuscarCatalogoView,
    CategoriaViewSet,
    CurrentUserView,
    DisponibilidadTurnoViewSet,
    LoginView,
    LogoutView,
    ProductoViewSet,
    SalaViewSet,
    ServicioViewSet,
    TurnoViewSet,
)
from api.views.root import ApiRootView


app_name = "api"

router = SimpleRouter()
router.register("categorias", CategoriaViewSet, basename="categoria")
router.register("productos", ProductoViewSet, basename="producto")
router.register("servicios", ServicioViewSet, basename="servicio")
router.register("salas", SalaViewSet, basename="sala")
router.register("disponibilidades", DisponibilidadTurnoViewSet, basename="disponibilidad")
router.register("turnos", TurnoViewSet, basename="turno")

urlpatterns = [
    path("", ApiRootView.as_view(), name="root"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("me/", CurrentUserView.as_view(), name="me"),
    path("buscar/", BuscarCatalogoView.as_view(), name="buscar"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="api:schema"), name="swagger-ui"),
    path("redoc/", SpectacularRedocView.as_view(url_name="api:schema"), name="redoc"),
    path("", include(router.urls)),
]
