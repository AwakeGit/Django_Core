import os
from pathlib import Path

from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Указание BASE_DIR для всей структуры проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Основные настройки проекта
SECRET_KEY = os.getenv("SECRET_KEY", "your-default-secret-key")
DEBUG = os.getenv("DEBUG", "False").lower() in ["true", "1", "yes"]
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost").split(",")

# Определение среды
ENVIRONMENT = os.getenv("DJANGO_ENV", "development").lower()

# Приложения
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Пользовательские приложения
    "apps.cart.apps.CartConfig",
    "apps.docs.apps.DocsConfig",
    "apps.users.apps.UsersConfig",
]

# Middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Настройки URL
ROOT_URLCONF = "config.urls"

# Настройки шаблонов
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
                "apps.users.context_processors.current_url_name",
            ],
        },
    },
]

# WSGI и ASGI
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Настройки базы данных
USE_SQLITE = os.getenv("USE_SQLITE", "True").lower() in ["true", "1", "yes"]

if USE_SQLITE:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME", "postgres"),
            "USER": os.getenv("DB_USER", "postgres"),
            "PASSWORD": os.getenv("DB_PASSWORD", "postgres"),
            "HOST": os.getenv("DB_HOST", "localhost"),
            "PORT": os.getenv("DB_PORT", "5432"),
        }
    }

# Валидация паролей
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Локализация
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Статические файлы и медиа
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Медиа
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Аутентификация
LOGIN_URL = "/users/login/"
LOGIN_REDIRECT_URL = "/"


# Логирование
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs/django_error.log",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "ERROR",
            "propagate": True,
        },
    },
}

# Специфические настройки для окружений
if ENVIRONMENT == "production":
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "True").lower() in [
        "true",
        "1",
        "yes",
    ]
    SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "31536000"))  # 1 год
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

    ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost").split(",")

elif ENVIRONMENT == "development":
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

elif ENVIRONMENT == "testing":
    DATABASES["default"]["NAME"] = (
        ":memory:" if USE_SQLITE else DATABASES["default"]["NAME"] + "_test"
    )
    DEBUG = False
