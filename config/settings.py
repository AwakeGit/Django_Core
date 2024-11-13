import os

from dotenv import load_dotenv

# Загрузка переменных окружения из .env
load_dotenv()

# Определение окружения
ENVIRONMENT = os.getenv("DJANGO_ENV", "development")

# Подключение соответствующего файла настроек
if ENVIRONMENT == "production":
    from .settings.production import *  # noqa: F401, F403
elif ENVIRONMENT == "testing":
    from .settings.testing import *  # noqa: F401, F403
else:
    from .settings.development import *  # noqa: F401, F403
