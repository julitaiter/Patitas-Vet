import django_filters

from app.models import DisponibilidadTurno, Producto, Servicio, Turno


class ProductoFilter(django_filters.FilterSet):
    precio_min = django_filters.NumberFilter(field_name="precio", lookup_expr="gte")
    precio_max = django_filters.NumberFilter(field_name="precio", lookup_expr="lte")

    class Meta:
        model = Producto
        fields = ["categoria", "activo", "destacado"]


class ServicioFilter(django_filters.FilterSet):
    precio_min = django_filters.NumberFilter(field_name="precio", lookup_expr="gte")
    precio_max = django_filters.NumberFilter(field_name="precio", lookup_expr="lte")

    class Meta:
        model = Servicio
        fields = ["categoria", "activo", "destacado"]


class DisponibilidadTurnoFilter(django_filters.FilterSet):
    class Meta:
        model = DisponibilidadTurno
        fields = ["servicio", "sala", "dia_semana", "activa"]


class TurnoFilter(django_filters.FilterSet):
    fecha_desde = django_filters.DateFilter(field_name="fecha", lookup_expr="gte")
    fecha_hasta = django_filters.DateFilter(field_name="fecha", lookup_expr="lte")

    class Meta:
        model = Turno
        fields = ["estado", "fecha", "servicio", "sala"]
