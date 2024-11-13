from .base import os

# Включение режима безопасности
DEBUG = False

# Дополнительные настройки безопасности
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "True") == "True"
SECURE_HSTS_SECONDS = 31536000  # Один год
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Настройки разрешенных хостов
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")
