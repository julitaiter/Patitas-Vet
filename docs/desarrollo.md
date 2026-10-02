# Desarrollo

[← Volver a la presentación](../README.md)

Esta guía reúne las notas técnicas que antes estaban en el README. No es necesaria para usar la página como cliente.

## Requisitos e instalación local

- Python 3.11 o superior y `pip`.
- Crear un entorno virtual e instalar `requirements.txt`.

En Windows:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

En Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

En Windows CMD, la activación es `venv\Scripts\activate`. El sitio local queda en `http://127.0.0.1:8000/` y el panel en `http://127.0.0.1:8000/admin/`. `makemigrations` se usa al cambiar modelos; no hace falta para instalar las migraciones ya incluidas.

### Datos de ejemplo

Para una base nueva y vacía, después de `migrate` se puede cargar un catálogo y una agenda de demostración:

```bash
python manage.py bootstrap_inicial
```

El comando crea cuatro categorías, cuatro productos, tres servicios, dos salas y quince disponibilidades semanales. Los nombres llevan `(demo)` y los precios/stock son ficticios; hay que revisarlos antes de mostrar el sitio a clientes. No crea usuarios, pedidos, datos bancarios, imágenes ni direcciones de tienda. Las preguntas frecuentes de ejemplo ya provienen de una migración.

No se ejecuta automáticamente. Si la base ya tiene catálogo o agenda, se detiene sin cambiar nada para evitar mezclar datos reales y de prueba. Solo si se desea añadir los ejemplos faltantes a esa base, ejecutar `python manage.py bootstrap_inicial --allow-existing`. En ambos casos conserva los registros ya existentes y puede repetirse sin duplicar los ejemplos.

## Configuración

`settings.py` lee un archivo `.env` opcional desde la raíz del proyecto. Para uso local hay valores por defecto; antes de desplegar, configurar al menos `SECRET_KEY`, `DEBUG=False` y `ALLOWED_HOSTS`. No guardar secretos reales en el repositorio.

La base de datos local usa SQLite por defecto. Se pueden configurar `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST` y `DB_PORT` para otra base. Los recursos estáticos y los archivos subidos usan, respectivamente, `STATIC_ROOT`/`STATIC_URL` y `MEDIA_ROOT`/`MEDIA_URL`. El entorno virtual y `media/` no se versionan; las plantillas se buscan también desde `templates/` en la raíz.

Las notificaciones de pedido usan `EMAIL_BACKEND` y las variables de correo `DEFAULT_FROM_EMAIL`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` y `EMAIL_USE_TLS`. **Por defecto se usa el backend de consola:** en desarrollo los mensajes se imprimen, no se entregan a una casilla. Configurar un backend real antes de depender del correo en producción.

Para comprobar el proyecto:

```bash
python manage.py check
python manage.py test
```

## Dependencias y API

Las dependencias principales incluyen Django, django-allauth, Django REST Framework, django-filter, drf-spectacular, Pillow, django-ckeditor y django-simple-history. Las versiones están fijadas en `requirements.txt`.

La API v1 está bajo `/api/v1/` y usa los modelos de dominio de `app` y `contacto`; `api` no mantiene modelos propios. La documentación interactiva está en `/api/v1/docs/`, `/api/v1/redoc/` y `/api/v1/schema/`. Acepta autenticación por token mediante `Authorization: Token <token>` y, según el cliente, sesión.

Rutas principales:

- `POST /api/v1/auth/registro/`, `POST /api/v1/auth/login/` y `POST /api/v1/auth/logout/`.
- `GET/PATCH /api/v1/me/`.
- `/api/v1/categorias/`, `/api/v1/productos/` y `/api/v1/servicios/`.
- `GET /api/v1/productos/{id}/stock/?cantidad=1` y `GET /api/v1/servicios/{id}/horarios/?fecha=YYYY-MM-DD`.
- `/api/v1/turnos/` y sus acciones de estado; `/api/v1/salas/` y `/api/v1/disponibilidades/` para personal autorizado.
- `GET /api/v1/buscar/?q=texto`, `/api/v1/consultas/` y `/api/v1/respuestas/`.

El catálogo admite lectura pública. Las escrituras de catálogo, salas y disponibilidades, y la gestión general de turnos y consultas, requieren personal autorizado. Los clientes autenticados solo acceden a sus propios turnos en la API. El historial de cambios del catálogo no se expone como endpoint.

## Catálogo e historial

`Producto` y `Servicio` heredan de `ItemCatalogo`, un modelo abstracto con nombre, descripción, precio, imagen y categoría. Cada uno mantiene su propia tabla y sus campos particulares, como stock o duración.

`django-simple-history` audita altas, modificaciones y bajas de esos dos modelos concretos. El historial se consulta desde el admin o en código: `producto.history.all()`, `producto.history.first()` y `Producto.history.all()`. Cada registro indica `history_user` cuando hay una petición autenticada y `history_type` (`+` alta, `~` cambio, `-` baja). `ItemCatalogo` y `Categoria` no tienen historial. La migración `0011_historicalproducto_historicalservicio` creó las tablas históricas, pero no reconstruye cambios anteriores. Fuera de una petición, el usuario puede quedar vacío. Las acciones masivas del admin y los cambios de stock del checkout generan registros; `QuerySet.update()` y `bulk_update()` por sí solos no los generan.

## SEO y contenido editorial

`/robots.txt` y `/sitemap.xml` están disponibles. El sitemap usa `django.contrib.sites` y contiene inicio, catálogo, preguntas frecuentes, contacto y detalles de productos y servicios activos. Las páginas privadas llevan `noindex`. El protocolo del sitemap es HTTPS. No hay una URL canónica automática: requiere reglas por página y parámetros antes de incorporarla.

Tras migrar, revisar **Admin → Sites → Sites** y configurar el dominio real del sitio con `SITE_ID=1`, sin protocolo, junto con `ALLOWED_HOSTS`. El README anterior mencionaba `jtaiter.com`; tratarlo como un dato a confirmar para cada despliegue, no como un dominio garantizado. Si el registro conserva `example.com`, editarlo en lugar de crear otro.

Las preguntas frecuentes se administran desde el panel. La migración inicial carga seis ejemplos editables. `django-ckeditor` y `ckeditor_uploader` sirven para su contenido; las cargas van a `MEDIA_ROOT/uploads/` y las rutas de carga/exploración requieren personal autorizado. Con `DEBUG=True`, Django sirve `/media/`; en producción hace falta servir `MEDIA_ROOT` y publicar recursos estáticos con `collectstatic`. `CKEDITOR_UPLOAD_PATH` y `CKEDITOR_CONFIGS` están en `settings.py`. No se configura `CKEDITOR_JQUERY_URL`; el sitio carga jQuery 3.7.1 para otras funciones.

**Advertencia de seguridad:** la versión incluida de `django-ckeditor` incorpora CKEditor 4.22.1, fuera de soporte. Limitar el acceso a personal autorizado y planificar su reemplazo antes de permitir edición a usuarios no confiables.

## Despliegue

El README anterior no incluía un procedimiento verificado para Gunicorn, Nginx o Docker. Este repositorio tampoco define aquí una guía de despliegue para esas herramientas; no se asume una configuración concreta. Antes de publicar, revisar secretos, dominio, correo, archivos estáticos y medios, base de datos y advertencias de `manage.py check --deploy`.
