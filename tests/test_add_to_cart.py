from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from apps.cart.models import Cart
from apps.docs.models import Docs


class AddToCartTest(TestCase):
    def setUp(self):
        # Создаем тестового пользователя и авторизуем его
        self.client = Client()
        self.username = "testuser"
        self.password = "testpassword"
        self.user = User.objects.create_user(
            username=self.username, password=self.password
        )
        self.client.login(username=self.username, password=self.password)

        # Создаем документ
        self.doc = Docs.objects.create(
            user=self.user, file="test_file.pdf", size=100, payment_status=False
        )

        # URL для добавления документа в корзину
        self.add_to_cart_url = reverse("add_to_cart", kwargs={"doc_id": self.doc.id})

    def test_unauthenticated_access(self):
        # Разлогиниваем пользователя
        self.client.logout()

        response = self.client.post(self.add_to_cart_url)

        # Проверяем, что неавторизованный пользователь перенаправляется на страницу входа
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_nonexistent_document(self):
        # Попытка добавления несуществующего документа
        nonexistent_url = reverse("add_to_cart", kwargs={"doc_id": 999})

        response = self.client.post(nonexistent_url)

        # Проверяем, что возвращается 404 ошибка
        self.assertEqual(response.status_code, 404)

    def test_already_paid_document(self):
        # Обновляем статус оплаты документа
        self.doc.payment_status = True
        self.doc.save()

        response = self.client.post(self.add_to_cart_url, follow=True)

        # Проверяем сообщение о том, что документ уже оплачен
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Этот документ уже оплачен.")

        # Проверяем, что документ не добавлен в корзину
        self.assertEqual(Cart.objects.filter(user=self.user, docs=self.doc).count(), 0)

    @patch("apps.cart.models.Cart.calculate_price")
    def test_successful_add_to_cart(self, mock_calculate_price):
        response = self.client.post(self.add_to_cart_url, follow=True)

        # Проверяем, что документ добавлен в корзину
        self.assertEqual(Cart.objects.filter(user=self.user, docs=self.doc).count(), 1)

        # Проверяем, что цена рассчитывается
        mock_calculate_price.assert_called_once()

        # Проверяем сообщение об успешном добавлении
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Документ добавлен в корзину.")

    def test_duplicate_add_to_cart(self):
        # Добавляем документ в корзину вручную
        Cart.objects.create(user=self.user, docs=self.doc)

        response = self.client.post(self.add_to_cart_url, follow=True)

        # Проверяем, что дубликат не был создан
        self.assertEqual(Cart.objects.filter(user=self.user, docs=self.doc).count(), 1)

        # Проверяем сообщение об успешном добавлении
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Документ добавлен в корзину.")
