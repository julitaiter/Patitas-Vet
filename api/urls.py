from rest_framework import routers
from .viewset import ServiciosApiViewSet

router = routers.SimpleRouter()
router.register(r'servicios', ServiciosApiViewSet, basename='servicios')

urlpatterns = router.urls