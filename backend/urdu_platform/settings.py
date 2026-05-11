"""
Urdu Education Platform — Django sozlamalari
Fan: Ma'lumotlar tuzilmasi va algoritmlar (MTA)
Muallif: Madaminov Uktamjon
"""
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

import os
from pathlib import Path
from decouple import config
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# Xavfsizlik
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# Ilovalar
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Uchinchi tomon
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    
    # Bizning ilovalar
    'apps.users',
    'apps.groups',
    'apps.courses',
    'apps.assessments',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Static fayllar uchun
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'urdu_platform.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'urdu_platform.wsgi.application'

# Ma'lumotlar bazasi
# Production: PostgreSQL (Render)
# Development: SQLite
# OLDIN:
import dj_database_url

_db_url = config('DATABASE_URL', default=None)

if _db_url:
    # Windows encoding muammosini hal qilish
    if isinstance(_db_url, bytes):
        _db_url = _db_url.decode('utf-8')
    DATABASES = {
        'default': dj_database_url.parse(
            _db_url,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
    # psycopg2 uchun encoding majburlash
    DATABASES['default']['OPTIONS'] = {
        'client_encoding': 'UTF8',
        'options': '-c client_encoding=UTF8'
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Maxsus foydalanuvchi modeli
AUTH_USER_MODEL = 'users.User'

# Parol tekshiruvi
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
]

# REST Framework sozlamalari
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# JWT Token sozlamalari
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),   # 8 soat
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),    # 7 kun
    'ROTATE_REFRESH_TOKENS': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# CORS sozlamalari (Frontend uchun)
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:5500,http://127.0.0.1:5500,http://localhost:3000'
).split(',')

# Lokal development uchun qo'shimcha
CORS_ALLOW_ALL_ORIGINS = True  # Faqat development uchun!

# Til va vaqt
LANGUAGE_CODE = 'uz'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

# Static va media fayllar
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Fayl yuklash cheklovlari
FILE_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024   # 100 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024    # 100 MB
