import os
from pathlib import Path
from decouple import config, Csv

# ============================================================================
# BASE DIRECTORY
# ============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================================================
# ENVIRONMENT
# ============================================================================
ENVIRONMENT = config('ENVIRONMENT', default='development')
DEBUG = config('DEBUG', default=False, cast=bool)

# For production on Cloud Run
if ENVIRONMENT == 'production':
    # Allow Cloud Run default domains (regional) and localhost
    ALLOWED_HOSTS = ['.run.app', 'localhost', '127.0.0.1']
else:
    ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# CSRF trusted origins (required for Django 4+ when behind HTTPS)
CSRF_TRUSTED_ORIGINS = ['https://*.run.app']

SECRET_KEY = config('SECRET_KEY', default='dev-key-not-secure')

# ============================================================================
# INSTALLED APPS
# ============================================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'drf_spectacular',
    'corsheaders',
    'django_filters',
    'core',
    'properties',
]

# ============================================================================
# MIDDLEWARE
# ============================================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ============================================================================
# TEMPLATES
# ============================================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ============================================================================
# ROOT URL CONFIGURATION
# ============================================================================
ROOT_URLCONF = 'pgadmin_config.urls'
WSGI_APPLICATION = 'pgadmin_config.wsgi.application'

# ============================================================================
# PASSWORD VALIDATORS
# ============================================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ============================================================================
# INTERNATIONALIZATION
# ============================================================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ============================================================================
# REST FRAMEWORK
# ============================================================================
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_AUTHENTICATION_CLASSES': ['core.auth.JWTAuthentication'],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
}

# ============================================================================
# SPECTACULAR (DRF Schema)
# ============================================================================
SPECTACULAR_SETTINGS = {
    'TITLE': 'pgAdmin API',
    'DESCRIPTION': 'Property Management API',
    'VERSION': '1.0.0',
    'CONTACT': {'name': 'Support', 'email': 'support@pgadmin.local'},
}

# ============================================================================
# DATABASE
# ============================================================================
_db_host = config('DATABASE_SOCKET', default=None)
if not _db_host:
    _db_host = config('DATABASE_HOST', default='localhost')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DATABASE_NAME', default='pgadmin_db'),
        'USER': config('DATABASE_USER', default='postgres'),
        'PASSWORD': config('DATABASE_PASSWORD', default=''),
        'HOST': _db_host,
        'PORT': config('DATABASE_PORT', default='5432'),
        # Connection pooling settings
        'CONN_MAX_AGE': 60,
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000',
        }
    }
}

# ============================================================================
# STATIC FILES
# ============================================================================
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ============================================================================
# CORS
# ============================================================================
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:8081',
    cast=Csv()
)

# ============================================================================
# SECURITY (Production)
# ============================================================================
if ENVIRONMENT == 'production':
    # Cloud Run terminates TLS at the edge; avoid redirect loops
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    # Respect proxy headers from Cloud Run/Load Balancer
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    USE_X_FORWARDED_HOST = True

# ============================================================================
# LOGGING
# ============================================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': config('LOG_LEVEL', default='INFO'),
        },
    },
}

# ============================================================================
# GOOGLE CLOUD STORAGE
# ============================================================================
GCS_BUCKET = config('GCS_BUCKET', default=None)
GCS_SIGNED_URL_EXPIRY = config('GCS_SIGNED_URL_EXPIRY', default=15 * 60, cast=int)
GCS_UPLOAD_PREFIX = config('GCS_UPLOAD_PREFIX', default='properties')

# Note: MIDDLEWARE is already defined above with the full stack including
# SecurityMiddleware, WhiteNoiseMiddleware, SessionMiddleware, CorsMiddleware,
# CommonMiddleware, CsrfViewMiddleware, AuthenticationMiddleware, MessageMiddleware,
# and XFrameOptionsMiddleware. Avoid redefining MIDDLEWARE below to prevent
# dropping required entries for admin, sessions, and messages.