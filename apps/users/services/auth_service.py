import logging

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpRequest

from apps.users.exceptions import ServiceError
from apps.users.forms import SimpleUserRegistrationForm

logger: logging = logging.getLogger("users")


class AuthService:
    """Сервис для работы с аутентификацией и регистрацией пользователей."""

    @staticmethod
    def login_user(request: HttpRequest, username: str, password: str) -> User:
        """
        Выполняет вход пользователя.

        :param request: HttpRequest объект
        :param username: Имя пользователя
        :param password: Пароль
        :raises ServiceError: Если аутентификация не удалась
        :return: Объект пользователя
        """
        logger.info(f"Попытка входа для пользователя: {username}")

        try:
            # Аутентификация пользователя
            user: User | None = authenticate(
                request, username=username, password=password
            )
            if user is None:
                logger.warning(f"Неудачная попытка входа для пользователя: {username}")
                raise ServiceError("Неправильное имя пользователя или пароль.")

            # Авторизация (создание сессии)
            login(request, user)
            logger.info(f"Успешный вход для пользователя: {username}")
            return user

        except ServiceError as e:
            logger.error(f"Ошибка входа для пользователя: {username}: {e.message}")
            raise

        except Exception:
            logger.exception(f"Неожиданная ошибка при входе пользователя {username}")
            raise ServiceError("Произошла неожиданная ошибка при входе.")

    @staticmethod
    def register_user(form: SimpleUserRegistrationForm) -> None:
        """
        Регистрирует нового пользователя.

        :param form: Форма регистрации пользователя
        :raises ServiceError: Если регистрация не удалась
        """

        if not form.is_valid():
            logger.warning("Неверные данные для регистрации.")
            raise ServiceError("Неверные данные для регистрации.")

        form.save()
        logger.info("Пользователь успешно зарегистрирован.")
