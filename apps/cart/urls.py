from django.urls import path

from .views import CartView

urlpatterns = [
    path("", CartView.as_view(), name="view_cart"),  # Отображение корзины
    path(
        "confirm-payment/<int:doc_id>/", CartView.as_view(), name="confirm_payment"
    ),  # Подтверждение оплаты
    path(
        "<str:action>/<int:doc_id>/", CartView.as_view(), name="cart_action"
    ),  # Действия с документом (add, remove)
    path(
        "<str:action>/", CartView.as_view(), name="cart_action"
    ),  # Действия с корзиной (confirm_all)
]
