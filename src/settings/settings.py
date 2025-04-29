import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(int(os.getenv("DEBUG", "0")))

# ALLOWED_HOSTS should be restricted in production
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-)hnv^!s8u=1f_yns=co5ho7d&)s@x=2=gxdf^*@n3m5hct7z(^"
    if DEBUG
    else "",
)

if not SECRET_KEY and not DEBUG:
    raise ValueError("SECRET_KEY environment variable is not set in production mode")

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "drf_spectacular",
    "rest_framework_simplejwt",
    "corsheaders",
    "defender",
    "user",
    "barter",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # Moved up for proper functionality
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "settings.disable_csrf.DisableCSRF",
    "user.middleware.CustomAuthenticationMiddleware",
    "defender.middleware.FailedLoginMiddleware",
]

# Security settings
if not DEBUG:
    # Enable only in production
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_REFERRER_POLICY = "same-origin"
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
DEFENDER_REDIS_URL = f"{REDIS_HOST}:{REDIS_PORT}"
DEFENDER_REDIS_NAME = "default"
DEFENDER_BEHIND_REVERSE_PROXY = True
DEFENDER_COOLOFF_TIME = 1200

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

ROOT_URLCONF = "settings.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "settings.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": str(os.getenv("POSTGRES_DB", "")),
        "USER": str(os.getenv("POSTGRES_USER", "")),
        "PASSWORD": str(os.getenv("POSTGRES_PASSWORD", "")),
        "HOST": str(os.getenv("POSTGRES_HOST", "localhost")),
        "PORT": str(os.getenv("POSTGRES_PORT", "5432")),
        "OPTIONS": {
            "connect_timeout": 5,
        },
        "CONN_MAX_AGE": 60,  # 1 minute connection persistence
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 10,  # Stronger password length requirement
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Кастомный пользователь и кастомная группа как основные модели
AUTH_USER_MODEL = "user.CustomUser"
AUTH_GROUP_MODEL = "user.AccessGroup"

LANGUAGE_CODE = "ru-RU"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True

LOGIN_URL = "/api/login/"
LOGOUT_URL = "/logout/"

STATIC_ROOT = BASE_DIR.parent / os.getenv("STATIC_PATH", "public/staticfiles/")
STATIC_URL = "static/"

MEDIA_ROOT = BASE_DIR.parent / os.getenv("MEDIA_PATH", "public/mediafiles/")
MEDIA_URL = "/media/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

TOKEN_SETTINGS = {
    "NAME": "token",
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=int(os.getenv("ACCESS_TOKEN_LIFETIME_MINUTES", "1440"))
    ),
    "TOTAL_ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=int(os.getenv("TOTAL_ACCESS_TOKEN_LIFETIME_MINUTES", "2880"))
    ),
    "ACCESS_COOKIE_HTTP_ONLY": True,  # Changed to True for security
    "ACCESS_COOKIE_SECURE": not DEBUG,  # Secure in production
    "ACCESS_COOKIE_SAMESITE": "Lax",  # Added SameSite policy
}

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication"
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "60/min",
        "user": "60/min",
    },
}

# Prioritize Argon2 as it's more secure
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {"level": "INFO", "handlers": ["file"]},
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "./logs/django-error.log",
            "formatter": "app",
            "maxBytes": 1024 * 1024 * 10,  # 10MB
            "backupCount": 10,
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "app",
        },
    },
    "loggers": {
        "django": {"handlers": ["file", "console"], "level": "INFO", "propagate": True},
        "django.server": {
            "handlers": ["file", "console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["file", "console"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "formatters": {
        "app": {
            "format": (
                "%(asctime)s [%(levelname)-8s] " "(%(module)s.%(funcName)s) %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
}

APPEND_SLASH = True

# CORS settings - restrict in production
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS = os.getenv(
        "CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")

CORS_ALLOW_CREDENTIALS = True

TG_SECRET = os.getenv("TG_SECRET", "")
BEARER_AUTH = bool(int(os.getenv("BEARER_AUTH", "1")))
COOKIE_AUTH = bool(int(os.getenv("COOKIE_AUTH", "0")))
BACKUPS = bool(int(os.getenv("BACKUPS", "0")))

# SESSION settings for improved security
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SAMESITE = "Lax"
