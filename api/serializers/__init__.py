from .auth import CurrentUserSerializer, LoginSerializer, RegisterSerializer
from .catalogo import (
    CategoriaSerializer,
    ProductoDetailSerializer,
    ProductoListSerializer,
    ServicioDetailSerializer,
    ServicioListSerializer,
)
from .salas import DisponibilidadTurnoSerializer, SalaSerializer
from .contacto import ConsultaCreateSerializer, ConsultaSerializer, RespuestaSerializer
from .common import (
    ApiRootSerializer,
    BusquedaCatalogoResponseSerializer,
    HorariosResponseSerializer,
    TokenResponseSerializer,
)
from .turnos import TurnoCreateSerializer, TurnoReadSerializer, TurnoStaffUpdateSerializer

__all__ = [
    "ApiRootSerializer",
    "BusquedaCatalogoResponseSerializer",
    "CategoriaSerializer",
    "CurrentUserSerializer",
    "HorariosResponseSerializer",
    "ConsultaCreateSerializer",
    "ConsultaSerializer",
    "DisponibilidadTurnoSerializer",
    "LoginSerializer",
    "ProductoDetailSerializer",
    "ProductoListSerializer",
    "RegisterSerializer",
    "RespuestaSerializer",
    "SalaSerializer",
    "ServicioDetailSerializer",
    "ServicioListSerializer",
    "TurnoCreateSerializer",
    "TurnoReadSerializer",
    "TurnoStaffUpdateSerializer",
    "TokenResponseSerializer",
]
