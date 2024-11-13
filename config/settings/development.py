from .base import BASE_DIR

# Включение режима отладки
DEBUG = True

# Установка хоста для разработки
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# База данных для разработки (например, SQLite)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Дополнительные настройки для разработки
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
