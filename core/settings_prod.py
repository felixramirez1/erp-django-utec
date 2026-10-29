# core/settings_prod.py
"""Configuración de producción — Render.com (versión final W03).

Hereda settings.py y sobreescribe todo lo necesario para producción.

Variables de entorno requeridas en Render Dashboard:
    SECRET_KEY              → clave aleatoria de ≥ 50 caracteres
    DATABASE_URL            → proporcionada automáticamente por Render PostgreSQL
    DJANGO_SETTINGS_MODULE  → core.settings_prod
    ALLOWED_HOSTS           → tu-app.onrender.com (o dejar vacío para auto)

Uso local con Docker:
    export DJANGO_SETTINGS_MODULE=core.settings_prod
    export SECRET_KEY=dev-clave-temporal
    export DATABASE_URL=postgres://erp_user:erp_pass@db:5432/erp_db
    gunicorn core.wsgi --bind 0.0.0.0:8000
"""
from .settings import *   # hereda toda la configuración base
import os
import dj_database_url

# ── SEGURIDAD BÁSICA ───────────────────────────────────────────────────────
DEBUG = False
SECRET_KEY = os.environ['SECRET_KEY']   # falla intencionalmente si no existe

# ── HOSTS PERMITIDOS ────────────────────────────────────────────────────────
# Render inyecta RENDER_EXTERNAL_HOSTNAME automáticamente
_render_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '')
_extra_hosts  = os.environ.get('ALLOWED_HOSTS', '').split(',')

ALLOWED_HOSTS = ['localhost', '127.0.0.1'] + (
    [_render_host] if _render_host else []
) + [h for h in _extra_hosts if h]

# ── BASE DE DATOS: PostgreSQL via DATABASE_URL ─────────────────────────────
DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600,          # conexiones persistentes 10 min
        conn_health_checks=True,   # verifica conexión antes de usarla
        ssl_require=True,          # Render requiere SSL en PostgreSQL
    )
}

# ── CSRF: dominios de confianza ────────────────────────────────────────────
CSRF_TRUSTED_ORIGINS = []
if _render_host:
    CSRF_TRUSTED_ORIGINS.append(f'https://{_render_host}')

# ── HEADERS HTTP SEGUROS ───────────────────────────────────────────────────
SECURE_SSL_REDIRECT            = True
SECURE_HSTS_SECONDS            = 31536000    # 1 año
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD            = True
SESSION_COOKIE_SECURE          = True
CSRF_COOKIE_SECURE             = True
X_FRAME_OPTIONS                = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF    = True
SECURE_REFERRER_POLICY         = 'same-origin'

# ── ARCHIVOS ESTÁTICOS ─────────────────────────────────────────────────────
# WhiteNoise ya configurado en settings.py; solo confirmar almacenamiento
STORAGES = {
       "default": {
           "BACKEND": "django.core.files.storage.FileSystemStorage",
       },
       "staticfiles": {
           "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
       },
   }

# ── LOGGING: solo WARNING y superiores en producción ──────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {'format': '[%(levelname)s] %(name)s: %(message)s'},
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django.security': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}
# core/settings_prod.py — agregar al final, después de los SECURE_* headers:

# ── ALMACENAMIENTO DE ARCHIVOS MEDIA (producción) ─────────────────────────
# Usar django-storages con S3 para persistir archivos entre deploys.
# Configurar estas variables en el dashboard de Render:
#   AWS_ACCESS_KEY_ID       → Access Key del bucket
#   AWS_SECRET_ACCESS_KEY   → Secret Key del bucket
#   AWS_STORAGE_BUCKET_NAME → Nombre del bucket
#   AWS_S3_REGION_NAME      → Región (ej. us-east-1)
#   AWS_S3_CUSTOM_DOMAIN    → Dominio CDN opcional

_bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME', '')

if _bucket:
    # Solo activa S3 si la variable de entorno está configurada
    DEFAULT_FILE_STORAGE  = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_ACCESS_KEY_ID     = os.environ.get('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
    AWS_STORAGE_BUCKET_NAME = _bucket
    AWS_S3_REGION_NAME    = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
    AWS_DEFAULT_ACL       = None        # el bucket controla el acceso
    AWS_S3_FILE_OVERWRITE = False       # no sobreescribir si el nombre ya existe
    AWS_QUERYSTRING_AUTH  = False       # URLs públicas (sin firma)
    MEDIA_URL             = f'https://{_bucket}.s3.amazonaws.com/'