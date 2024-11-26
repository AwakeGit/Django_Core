import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views import View

from apps.cart.exceptions import ServiceError
from apps.cart.services.payment_service import CartService

logger = logging.getLogger("cart")


class CartView(LoginRequiredMixin, View):
    """
    Представление для работы с корзиной.
    """

    def post(
        self, request: HttpRequest, action: str, doc_id: int = None
    ) -> HttpResponse:
        """
        Обрабатывает POST-запросы для действий с корзиной.

        :param request: Объект запроса.
        :param action: Действие, которое нужно выполнить (add, confirm, remove, confirm_all).
        :param doc_id: ID документа (если применимо).
        :return: Перенаправление с результатом выполнения действия.
        """
        cart_service = CartService()

        try:
            if action == "add" and doc_id is not None:
                cart_service.add_to_cart(request.user, doc_id)
                messages.success(request, "Документ добавлен в корзину.")
            elif action == "confirm" and doc_id is not None:
                cart_service.confirm_payment(request.user, doc_id)
                messages.success(request, "Оплата успешно выполнена!")
            elif action == "remove" and doc_id is not None:
                cart_service.remove_from_cart(request.user, doc_id)
                messages.success(request, "Документ удалён из корзины.")
            elif action == "confirm_all":
                cart_service.confirm_all_payments(request.user)
                messages.success(request, "Оплата всех документов успешно выполнена!")
            else:
                messages.error(
                    request, "Действие не поддерживается или отсутствует doc_id."
                )
            return redirect("view_cart")

        except ServiceError as e:
            logger.error(f"Ошибка при выполнении действия {action}: {e.message}")
            messages.error(request, e.message)
            return redirect("view_cart")

        except Exception:
            logger.exception(f"Неожиданная ошибка при выполнении действия {action}.")
            messages.error(request, "Произошла ошибка. Попробуйте позже.")
            return redirect("view_cart")

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Отображает содержимое корзины пользователя.

        :param request: Объект запроса.
        :return: HTTP-ответ с отображением корзины.
        """
        cart_service = CartService()

        # Получаем элементы корзины
        cart_items = cart_service.view_cart(request.user)
        total_price = sum(item.order_price for item in cart_items)

        return render(
            request,
            "cart/cart.html",
            {
                "cart_items": cart_items,
                "total_price": total_price,
            },
        )
