from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from apps.cart.models import Cart
from apps.docs.models import Docs


class ConfirmPaymentTest(TestCase):
    def setUp(self):
        # Создаем тестового пользователя и авторизуем его
        self.client = Client()
        self.username = "testuser"
        self.password = "testpassword"
        self.user = User.objects.create_user(
            username=self.username, password=self.password
        )
        self.client.login(username=self.username, password=self.password)

        # Создаем документ и добавляем его в корзину
        self.doc = Docs.objects.create(
            user=self.user, file="test_file.pdf", size=100, payment_status=False
        )
        self.cart_item = Cart.objects.create(user=self.user, docs=self.doc)

        # URL для подтверждения оплаты
        self.confirm_payment_url = reverse(
            "confirm_payment", kwargs={"doc_id": self.doc.id}
        )

    def test_unauthenticated_access(self):
        # Разлогиниваем пользователя
        self.client.logout()

        response = self.client.get(self.confirm_payment_url)

        # Проверяем, что неавторизованный пользователь перенаправляется на страницу входа
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_document_payment_status_update(self):
        self.client.get(self.confirm_payment_url)

        # Проверяем, что статус оплаты обновился
        self.doc.refresh_from_db()
        self.assertTrue(self.doc.payment_status)

    def test_document_removed_from_cart(self):
        self.client.get(self.confirm_payment_url)

        # Проверяем, что документ удален из корзины
        self.assertEqual(Cart.objects.filter(user=self.user, docs=self.doc).count(), 0)

    def test_success_message(self):
        response = self.client.get(self.confirm_payment_url, follow=True)

        # Проверяем сообщение об успешной оплате
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Оплата успешно выполнена!")

    def test_nonexistent_document(self):
        nonexistent_url = reverse("confirm_payment", kwargs={"doc_id": 999})

        response = self.client.get(nonexistent_url)

        # Проверяем, что возвращается 404 ошибка
        self.assertEqual(response.status_code, 404)
