from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from apps.cart.models import Cart
from apps.docs.models import Docs


class ConfirmAllPaymentsTest(TestCase):
    def setUp(self):
        # Создаем тестового пользователя и авторизуем его
        self.client = Client()
        self.username = "testuser"
        self.password = "testpassword"
        self.user = User.objects.create_user(
            username=self.username, password=self.password
        )
        self.client.login(username=self.username, password=self.password)

        # Создаем несколько документов
        self.docs = [
            Docs.objects.create(
                user=self.user,
                file=f"test_file_{i}.pdf",
                size=100,
                payment_status=False,
            )
            for i in range(3)
        ]

        # Добавляем документы в корзину
        self.cart_items = [
            Cart.objects.create(user=self.user, docs=doc, payment=False)
            for doc in self.docs
        ]

        # URL для подтверждения всех оплат
        self.confirm_all_payments_url = reverse("confirm_all_payments")

    def test_unauthenticated_access(self):
        # Разлогиниваем пользователя
        self.client.logout()

        response = self.client.post(self.confirm_all_payments_url)

        # Проверяем, что неавторизованный пользователь перенаправляется на страницу входа
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_payment_status_updated(self):
        self.client.post(self.confirm_all_payments_url)

        # Проверяем, что статус оплаты всех элементов корзины обновился
        for item in self.cart_items:
            item.refresh_from_db()
            self.assertTrue(item.payment)

        # Проверяем, что статус оплаты документов также обновился
        for doc in self.docs:
            doc.refresh_from_db()
            self.assertTrue(doc.payment_status)

    def test_success_message(self):
        response = self.client.post(self.confirm_all_payments_url, follow=True)

        # Проверяем сообщение об успешной оплате
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Оплата успешно выполнена!")

    def test_only_post_method_allowed(self):
        response = self.client.get(self.confirm_all_payments_url)

        # Проверяем, что GET-запрос не поддерживается (можно вернуть 405 или редирект)
        self.assertEqual(response.status_code, 405)  # Метод не разрешен

    def test_no_cart_items(self):
        # Удаляем все элементы из корзины
        Cart.objects.all().delete()

        response = self.client.post(self.confirm_all_payments_url, follow=True)

        # Проверяем, что сообщение об успешной оплате все равно отображается
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Оплата успешно выполнена!")
