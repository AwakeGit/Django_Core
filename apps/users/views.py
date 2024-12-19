import logging

import requests
from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views import View

from apps.users.exceptions import ServiceError
from apps.users.forms import SimpleUserRegistrationForm
from apps.users.services.auth_service import AuthService

logger = logging.getLogger("users")


class LoginView(View):
    """Представление для входа пользователя."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Отображает форму входа.

        :param request: Объект запроса.
        :return: HTTP-ответ с формой входа.
        """
        logger.info("Вызвался GET-запрос для входа пользователя.")
        return render(request, "auth/login.html", {})

    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Обрабатывает отправку данных для входа пользователя.

        :param request: Объект запроса.
        :return: Перенаправление на главную страницу или форма с ошибкой.
        """
        logger.info("Вызвался POST-запрос для входа пользователя.")
        username: str | None = request.POST.get("username")
        password: str | None = request.POST.get("password")
        logger.info(f"Попытка входа для пользователя: {username}")

        # try:
        #     if username is None or password is None:
        #         raise ServiceError("Имя пользователя и пароль обязательны.")
        #     AuthService.login_user(request, username, password)
        #     logger.info(f"Успешный вход для пользователя: {username}")
        #     return redirect("main")
        #
        # except ServiceError as e:
        #     logger.error(f"Ошибка входа: {e.message}")
        #     messages.error(request, e.message)
        #     return render(request, "auth/login.html", {"error_message": e.message})
        #
        # except Exception:
        #     logger.exception("Произошла неожиданная ошибка в LoginView.")
        #     messages.error(request, "Произошла ошибка. Попробуйте позже.")
        #     return render(
        #         request,
        #         "auth/login.html",
        #         {"error_message": "Произошла ошибка. Попробуйте позже."},
        #     )
        if not username or not password:
            messages.error(request, "Имя пользователя и пароль обязательны.")
            return render(
                request,
                "auth/login.html",
                {"error_message": "Имя пользователя и пароль обязательны."},
            )

        try:
            # Аутентификация пользователя
            AuthService.login_user(request, username, password)
            logger.info(f"Успешный вход для пользователя: {username}")

            # Запрос к DRF Proxy для получения токена
            proxy_url = f"{settings.DRF_PROXY_URL}/api/token/"
            data = {"username": username, "password": password}
            headers = {"Content-Type": "application/json"}

            response = requests.post(proxy_url, json=data, headers=headers)
            if response.status_code == 200:
                token = response.json().get("access")
                request.session["auth_token"] = token
                logger.info(f"Токен успешно получен для пользователя {username}.")
            else:
                logger.error(
                    f"Ошибка получения токена: {response.status_code} {response.text}"
                )
                messages.error(request, "Не удалось получить токен. Попробуйте позже.")
                return render(
                    request,
                    "auth/login.html",
                    {"error_message": "Ошибка аутентификации."},
                )

            return redirect("main")

        except Exception as e:
            logger.exception("Произошла ошибка при обработке запроса входа.")
            messages.error(request, "Произошла ошибка. Попробуйте позже.")
            return render(request, "auth/login.html", {"error_message": str(e)})


class RegisterView(View):
    """Представление для регистрации пользователя."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Отображает форму регистрации.

        :param request: Объект запроса.
        :return: HTTP-ответ с формой регистрации.
        """

        logger.info("Вызвался GET-запрос для регистрации пользователя.")
        form = SimpleUserRegistrationForm()
        return render(request, "auth/register.html", {"form": form})

    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Обрабатывает отправку данных для регистрации пользователя.

        :param request: Объект запроса.
        :return: Перенаправление на главную страницу или форма с ошибкой.
        """

        logger.info("Вызвался POST-запрос для регистрации пользователя.")
        form = SimpleUserRegistrationForm(request.POST)

        try:
            AuthService.register_user(form)
            logger.info("Пользователь успешно зарегистрирован.")
            messages.success(request, "Вы успешно зарегистрировались!")
            return redirect("main")

        except ServiceError as e:
            logger.error(f"Ошибка регистрации: {e.message}")
            messages.error(request, e.message)
            return render(
                request,
                "auth/register.html",
                {"form": form, "error_message": e.message},
            )

        except Exception:
            logger.exception("Произошла неожиданная ошибка в RegisterView.")
            messages.error(request, "Произошла ошибка. Попробуйте позже.")
            return render(
                request,
                "auth/register.html",
                {"form": form, "error_message": "Произошла ошибка. Попробуйте позже."},
            )
