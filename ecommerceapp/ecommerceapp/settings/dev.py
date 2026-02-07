import os
import dj_database_url
from pathlib import Path
from decouple import config # Simplified import

# 1. PATH CONFIGURATION
# dev.py is at: ecommerceapp/ecommerceapp/settings/dev.py
# .parent.parent.parent gets us to the root where manage.py lives
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 2. CORE SECURITY
SECRET_KEY = config("DJANGO_SECRET_KEY", default="django-insecure-dev-key")
DEBUG = True 
ALLOWED_HOSTS = config("DJANGO_ALLOWED_HOSTS", default="localhost,127.0.0.1,django_admin,nginx_gateway").split(",")

# 3. APP DEFINITION
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_filters",
    "corsheaders",
    "store",  # Your custom app
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware", # For static files
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# 4. ROUTING & WSGI
ROOT_URLCONF = "ecommerceapp.urls"
WSGI_APPLICATION = "ecommerceapp.wsgi.application"

# 5. TEMPLATES
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

# 6. DATABASE
# Inside Docker, we use the service name 'db'
DATABASES = {
    'default': dj_database_url.config(
        default=config(
            "DATABASE_URL",
            default="postgres://postgres:postgres@db:5432/ecommerce_db"
        ),
        conn_max_age=600,
    )
}

# 7. CACHE & SESSIONS (Redis-Free Fallback)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}
SESSION_ENGINE = "django.contrib.sessions.backends.db"

# 8. STATIC & MEDIA
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []
# Using standard storage for dev to avoid manifest errors during initial boot
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# 9. CORS & CSRF
CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", default="http://localhost:3000").split(",")
CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default="http://localhost:8000,http://127.0.0.1:8000").split(",")

# 10. INTERNATIONALIZATION
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'