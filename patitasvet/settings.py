"""
Django settings for patitasvet project.

Configuracion basada en variables de entorno desde un archivo .env.
Requiere instalar python-dotenv:
    pip install python-dotenv
"""

import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


def env_bool(name, default=False):
    value = os.getenv(name)

    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on", "si", "sí"}


def env_list(name, default=None):
    value = os.getenv(name)

    if value is None:
        return default or []

    return [item.strip() for item in value.split(",") if item.strip()]


def env_path(name, default):
    value = os.getenv(name, default)
    path = Path(value)

    if path.is_absolute():
        return path

    return BASE_DIR / path


SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-cambiar-esta-clave")
DEBUG = env_bool("DEBUG", default=True)
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", default=["127.0.0.1", "localhost"])


INSTALLED_APPS = [
    # "sslserver",
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.sitemaps",

    # Librerias de terceros
    "captcha",
    "rest_framework",
    "rest_framework.authtoken",
    "django_filters",
    "drf_spectacular",
    "ckeditor",
    "ckeditor_uploader",

    # Apps propias
    "app",
    "contacto.apps.ContactoConfig",
    "api.apps.ApiConfig",

    # Allauth
    "allauth",
    "allauth.account",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "patitasvet.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "patitasvet.wsgi.application"


DB_ENGINE = os.getenv("DB_ENGINE", "django.db.backends.sqlite3")
DB_NAME = os.getenv("DB_NAME", "db.sqlite3")

if DB_ENGINE == "django.db.backends.sqlite3":
    database_name = Path(DB_NAME)

    if not database_name.is_absolute():
        database_name = BASE_DIR / database_name

    DATABASES = {
        "default": {
            "ENGINE": DB_ENGINE,
            "NAME": database_name,
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": DB_ENGINE,
            "NAME": DB_NAME,
            "USER": os.getenv("DB_USER", ""),
            "PASSWORD": os.getenv("DB_PASSWORD", ""),
            "HOST": os.getenv("DB_HOST", ""),
            "PORT": os.getenv("DB_PORT", ""),
        }
    }


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "es-ar"
TIME_ZONE = "America/Argentina/Buenos_Aires"
USE_I18N = True
USE_TZ = True


STATIC_URL = os.getenv("STATIC_URL", "/static/")
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = env_path("STATIC_ROOT", "staticfiles")

MEDIA_URL = os.getenv("MEDIA_URL", "/media/")
MEDIA_ROOT = env_path("MEDIA_ROOT", "media")

# django-ckeditor carga archivos mediante el storage de Django (MEDIA_ROOT/uploads/).
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_CONFIGS = {
    "default": {
        "toolbar": "PatitasVet",
        "toolbar_PatitasVet": [
            ["Source"],
            ["Format", "Styles"],
            ["Bold", "Italic", "Underline", "Strike", "RemoveFormat"],
            ["NumberedList", "BulletedList", "Outdent", "Indent", "Blockquote"],
            ["Link", "Unlink", "Image", "Table", "HorizontalRule"],
            ["JustifyLeft", "JustifyCenter", "JustifyRight"],
            ["SpecialChar", "Maximize"],
        ],
        "height": 300,
        "width": "100%",
    },
}


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
SITE_ID = 1

CHECKOUT_DRAFT_TTL = int(os.getenv("CHECKOUT_DRAFT_TTL", "7200"))
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "Patitas Vet <no-reply@patitasvet.local>")
EMAIL_HOST = os.getenv("EMAIL_HOST", "localhost")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", default=True)


AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

LOGIN_REDIRECT_URL = os.getenv("LOGIN_REDIRECT_URL", "/")
ACCOUNT_LOGOUT_REDIRECT_URL = os.getenv("ACCOUNT_LOGOUT_REDIRECT_URL", "/")
ACCOUNT_EMAIL_VERIFICATION = os.getenv("ACCOUNT_EMAIL_VERIFICATION", "none")
ACCOUNT_ADAPTER = os.getenv("ACCOUNT_ADAPTER", "app.adapters.AccountAdapter")

ACCOUNT_SIGNUP_FIELDS = [
    "username*",
    "email*",
    "password1*",
    "password2*",
]

ACCOUNT_LOGIN_METHODS = set(
    env_list("ACCOUNT_LOGIN_METHODS", default=["username", "email"]))

# Django REST Framework

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "api.pagination.StandardResultsSetPagination",
    "PAGE_SIZE": int(os.getenv("API_PAGE_SIZE", "20")),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}


# OpenAPI / Swagger / ReDoc

SPECTACULAR_SETTINGS = {
    "TITLE": "Patitas Vet API",
    "DESCRIPTION": "API REST v1 de Patitas Vet.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "ENUM_NAME_OVERRIDES": {
        "TurnoEstadoEnum": "app.models.Turno.ESTADOS",
        "ConsultaEstadoEnum": "contacto.models.Consulta.ESTADO_CHOICES",
    },
}
