from . import base

STATIC_URL = base.STATIC_URL
STATICFILES_DIRS = base.STATICFILES_DIRS
BASE_DIR = base.BASE_DIR
INSTALLED_APPS = base.INSTALLED_APPS
MIDDLEWARE = base.MIDDLEWARE
TEMPLATES = base.TEMPLATES
AUTH_PASSWORD_VALIDATORS = base.AUTH_PASSWORD_VALIDATORS
ROOT_URLCONF = base.ROOT_URLCONF
SECRET_KEY = base.SECRET_KEY

# Включение режима отладки
DEBUG = True

# Установка хоста для разработки
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# База данных для разработки (например, SQLite)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Дополнительные настройки для разработки
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
