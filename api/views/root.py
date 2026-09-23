from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView


class ApiRootView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {
                "version": "v1",
                "auth_login": reverse("api:login", request=request),
                "me": reverse("api:me", request=request),
                "categorias": reverse("api:categoria-list", request=request),
                "productos": reverse("api:producto-list", request=request),
                "servicios": reverse("api:servicio-list", request=request),
                "salas": reverse("api:sala-list", request=request),
                "disponibilidades": reverse("api:disponibilidad-list", request=request),
                "turnos": reverse("api:turno-list", request=request),
                "buscar": reverse("api:buscar", request=request),
                "schema": reverse("api:schema", request=request),
                "docs": reverse("api:swagger-ui", request=request),
            }
        )
