import os
import dj_database_url
from decouple import Config, RepositoryEnv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Always load .env.dev for development
config = Config(RepositoryEnv(BASE_DIR / ".env.dev"))

# Core security
SECRET_KEY = config("DJANGO_SECRET_KEY", default="django-insecure-dev-key")
DEBUG = True   # Always True in dev
ALLOWED_HOSTS = config("DJANGO_ALLOWED_HOSTS", default="localhost,127.0.0.1").split(",")

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
    "store",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
# ecommerceapp/ecommerceapp/settings/dev.py
from pathlib import Path

# 1. Updated BASE_DIR to reach the project root (3 levels up from dev.py)
# dev.py (file) -> settings (parent) -> ecommerceapp (parent) -> root (parent)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ... other settings ...

# 2. Updated TEMPLATES configuration
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # This now correctly points to the 'templates' folder next to manage.py
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

# Database
DATABASES = {
    'default': dj_database_url.config(
        default=config(
            "DATABASE_URL",
            default="postgres://postgres:God4me%402025@localhost:5432/store_db"
        ),
        conn_max_age=600,
    )
}

# --- REDIS IS DOWN FIX ---
# Switch from Redis to Local Memory Cache
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}

# Switch from Redis Cache Sessions to Database Sessions
# This prevents the "Unending Processing" loop caused by Redis timeouts
SESSION_ENGINE = "django.contrib.sessions.backends.db"
# -------------------------

# Static and Media
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Email (Console backend so you can see emails in your terminal)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# CORS & CSRF
CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", default="http://localhost:3000").split(",")
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:8000', 'http://localhost:8000']

# Dev Security - NO REDIRECTS
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = None

ROOT_URLCONF = "ecommerceapp.urls"
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'