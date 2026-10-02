# Patitas Vet

Proyecto web desarrollado con Django para una veterinaria.

## Requisitos

- Python 3.11 o superior
- pip

## Instalación con entorno virtual

### 1. Crear el entorno virtual

En Windows:

```bash
python -m venv venv
```

En Linux/macOS:

```bash
python3 -m venv venv
```

### 2. Activar el entorno virtual

En Windows PowerShell:

```bash
.\venv\Scripts\Activate.ps1
```

En Windows CMD:

```bash
venv\Scripts\activate
```

En Linux/macOS:

```bash
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Aplicar migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Crear un superusuario

```bash
python manage.py createsuperuser
```

### 6. Ejecutar el servidor

```bash
python manage.py runserver
```

Luego abrir en el navegador:

```text
http://127.0.0.1:8000/
```

Panel de administración:

```text
http://127.0.0.1:8000/admin/
```

## Dependencias principales

- Django
- django-allauth
- Django REST Framework
- django-filter
- drf-spectacular
- Pillow
- django-simple-history

## API REST v1

La API está disponible bajo `/api/v1/` y reutiliza exclusivamente los modelos
de dominio de `app.models` y `contacto.models`. La app `api` no define ni
mantiene modelos propios.

Documentación interactiva:

- Swagger UI: `http://127.0.0.1:8000/api/v1/docs/`
- ReDoc: `http://127.0.0.1:8000/api/v1/redoc/`
- Esquema OpenAPI: `http://127.0.0.1:8000/api/v1/schema/`

Autenticación por token:

```http
Authorization: Token <token>
```

Endpoints principales:

- `POST /api/v1/auth/registro/`
- `POST /api/v1/auth/login/`
- `POST /api/v1/auth/logout/`
- `GET/PATCH /api/v1/me/`
- `/api/v1/categorias/`, `/productos/` y `/servicios/`
- `GET /api/v1/productos/{id}/stock/?cantidad=1`
- `GET /api/v1/servicios/{id}/horarios/?fecha=YYYY-MM-DD`
- `/api/v1/turnos/` y sus acciones `cancelar`, `confirmar`, `realizar` y `pendiente`
- `/api/v1/salas/` y `/disponibilidades/` para staff
- `GET /api/v1/buscar/?q=texto`
- `POST /api/v1/consultas/` público; gestión de consultas y respuestas para staff

El catálogo admite lectura pública. Las escrituras de catálogo, salas,
disponibilidades y la gestión global de turnos requieren un usuario staff. Un
cliente autenticado solo puede consultar, crear y cancelar sus propios turnos.

## Modelos

`Producto` y `Servicio` comparten los mismos campos, por eso se creó el modelo abstracto `ItemCatalogo`.

Ese modelo contiene los campos comunes:

- `nombre`
- `descripcion`
- `precio`
- `imagen`
- `categoria`

Luego `Producto` y `Servicio` heredan de `ItemCatalogo`, evitando duplicar código y manteniendo dos tablas separadas en la base de datos.

### Historial del catálogo

`Producto` y `Servicio` registran altas, modificaciones y bajas mediante
`django-simple-history`. La auditoría se consulta desde el enlace **Historial**
de cada objeto en el panel de administración, con los permisos habituales del
admin. No se publica por la API ni por el catálogo público. `ItemCatalogo` y
`Categoria` no tienen historial.

La migración `0011_historicalproducto_historicalservicio` crea las tablas
históricas; no reconstruye cambios anteriores. El usuario queda registrado
cuando el cambio ocurre dentro de una petición autenticada. Las operaciones
ejecutadas sin petición (por ejemplo, scripts) pueden figurar sin usuario.
Las acciones masivas del admin y los descuentos/reintegros de stock del checkout
generan registros. Si se agregan otros cambios masivos, tener en cuenta que
`QuerySet.update()` y `bulk_update()` por sí solos no generan historial.

Desde el shell se puede consultar `producto.history.all()` o el último cambio
con `producto.history.first()`. Para consultar todos los productos históricos,
usar `Producto.history.all()`. Cada registro expone `history_user` y
`history_type`: `+` para creación, `~` para modificación y `-` para eliminación.

## Notas

## SEO técnico

- `robots.txt`: `/robots.txt`; sitemap: `/sitemap.xml` (en producción, `https://jtaiter.com/robots.txt` y `https://jtaiter.com/sitemap.xml`).
- Después de migrar, revisar **Admin → Sites → Sites** y editar el Site con ID `1`: **Domain name** `jtaiter.com` (sin `https://`) y **Display name** `Patitas Vet`. Si aparece `example.com`, editar ese registro en lugar de crear otro. También incluir el dominio en `ALLOWED_HOSTS` del entorno de producción.
- El sitemap toma el dominio de `django.contrib.sites` y publica solo inicio, catálogo, contacto y detalles activos de productos y servicios. Las páginas privadas llevan `noindex` y no aparecen en el sitemap.
- Los sitemaps usan HTTPS. No se agregó canonical automático: una URL canónica correcta depende de la página y de sus parámetros; se puede incorporar por plantilla cuando se definan esas reglas.

## Preguntas frecuentes y CKEditor

- La página pública está en `/preguntas-frecuentes/`. Las preguntas se administran en **Admin → App → Preguntas frecuentes**; la migración inicial carga seis ejemplos editables.
- `django-ckeditor` y `ckeditor_uploader` están instalados. Los archivos se guardan mediante `MEDIA_ROOT` bajo `uploads/` y se sirven con `MEDIA_URL`; las rutas de carga y exploración requieren un usuario staff. En desarrollo Django sirve `/media/` con `DEBUG=True`; en producción hay que asegurar que el servidor web sirva `MEDIA_ROOT` y ejecutar `collectstatic` para los recursos del editor.
- `CKEDITOR_UPLOAD_PATH` y `CKEDITOR_CONFIGS` están en `settings.py`. No se configura `CKEDITOR_JQUERY_URL`: esta versión inicializa el editor con JavaScript propio y el sitio ya carga jQuery 3.7.1 para otras funciones.
- **Advertencia de seguridad:** `django-ckeditor` 6.7.3 incorpora CKEditor 4.22.1, fuera de soporte y con problemas de seguridad conocidos. Se conserva porque fue la librería solicitada. Limitar el acceso staff y evaluar una migración futura a un editor mantenido antes de usar contenido de editores no confiables.

- El entorno virtual no se sube al repositorio. Cada persona debe crearlo localmente con `python -m venv venv`.
- Las imágenes cargadas se guardan en la carpeta `media/`, que también está excluida del repositorio.
- Los templates del proyecto están configurados desde la carpeta raíz `templates/`.
