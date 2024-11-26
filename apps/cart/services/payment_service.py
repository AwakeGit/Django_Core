from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from apps.cart.exceptions import ServiceError
from apps.cart.models import Cart
from apps.docs.models import Docs


class CartService:
    """
    Сервис для работы с корзиной пользователя.
    """

    @staticmethod
    def confirm_payment(user: User, doc_id: int) -> None:
        """
        Подтверждает оплату документа и удаляет его из корзины.

        :param user: Пользователь, который совершает оплату.
        :param doc_id: ID оплачиваемого документа.
        :raises ServiceError: Если документ не найден или принадлежит другому пользователю.
        """
        try:
            doc = get_object_or_404(Docs, id=doc_id, user=user)
        except Exception:
            raise ServiceError("Документ не найден или у вас нет прав на него.")

        doc.payment_status = True
        doc.save()

        Cart.objects.filter(user=user, docs=doc).delete()

    @staticmethod
    def add_to_cart(user: User, doc_id: int) -> None:
        """
        Добавляет документ в корзину.

        :param user: Пользователь, который добавляет документ.
        :param doc_id: ID документа для добавления.
        :raises ServiceError: Если документ уже оплачен или уже находится в корзине.
        """
        doc = get_object_or_404(Docs, id=doc_id, user=user)

        if doc.payment_status:
            raise ServiceError("Этот документ уже оплачен.")

        cart_item, created = Cart.objects.get_or_create(user=user, docs=doc)

        if created:
            cart_item.calculate_price()

    @staticmethod
    def remove_from_cart(user: User, doc_id: int) -> None:
        """
        Удаляет документ из корзины.

        :param user: Пользователь, который удаляет документ.
        :param doc_id: ID документа для удаления.
        :raises ServiceError: Если документ не найден в корзине.
        """
        cart_item = get_object_or_404(Cart, user=user, docs_id=doc_id)

        # Удаляем документ из корзины
        cart_item.delete()

    @staticmethod
    def view_cart(user: User) -> QuerySet:
        """
        Возвращает содержимое корзины текущего пользователя.

        :param user: Пользователь, для которого возвращается содержимое корзины.
        :return: QuerySet с элементами корзины.
        """
        return Cart.objects.filter(user=user, payment=False)

    @staticmethod
    def confirm_all_payments(user: User) -> None:
        """
        Подтверждает оплату всех неоплаченных элементов корзины пользователя.

        :param user: Пользователь, который совершает оплату.
        """
        cart_items = Cart.objects.filter(user=user, payment=False)

        for item in cart_items:
            # Помечаем элемент корзины как оплаченный
            item.payment = True
            item.save()

            # Обновляем статус оплаты документа
            doc = item.docs
            doc.payment_status = True
            doc.save()
