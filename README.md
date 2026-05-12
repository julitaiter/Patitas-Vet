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
- Pillow

## Modelos

`Producto` y `Servicio` comparten los mismos campos, por eso se creó el modelo abstracto `ItemCatalogo`.

Ese modelo contiene los campos comunes:

- `nombre`
- `descripcion`
- `precio`
- `imagen`
- `categoria`

Luego `Producto` y `Servicio` heredan de `ItemCatalogo`, evitando duplicar código y manteniendo dos tablas separadas en la base de datos.

## Notas

- El entorno virtual no se sube al repositorio. Cada persona debe crearlo localmente con `python -m venv venv`.
- Las imágenes cargadas se guardan en la carpeta `media/`, que también está excluida del repositorio.
- Los templates del proyecto están configurados desde la carpeta raíz `templates/`.
