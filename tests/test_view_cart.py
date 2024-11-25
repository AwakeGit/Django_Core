from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from apps.cart.models import Cart
from apps.docs.models import Docs


class ViewCartTest(TestCase):
    def setUp(self):
        # Создаем тестового пользователя и авторизуем его
        self.client = Client()
        self.username = "testuser"
        self.password = "testpassword"
        self.user = User.objects.create_user(
            username=self.username, password=self.password
        )
        self.client.login(username=self.username, password=self.password)

        # Создаем документы
        self.doc1 = Docs.objects.create(user=self.user, file="test_file1.pdf", size=100)
        self.doc2 = Docs.objects.create(user=self.user, file="test_file2.pdf", size=200)

        # Добавляем документы в корзину
        self.cart_item1 = Cart.objects.create(
            user=self.user, docs=self.doc1, order_price=50.0, payment=False
        )
        self.cart_item2 = Cart.objects.create(
            user=self.user, docs=self.doc2, order_price=75.0, payment=False
        )

        # URL для отображения корзины
        self.view_cart_url = reverse("view_cart")

    def test_unauthenticated_access(self):
        # Разлогиниваем пользователя
        self.client.logout()

        response = self.client.get(self.view_cart_url)

        # Проверяем, что неавторизованный пользователь перенаправляется на страницу входа
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_view_cart_items(self):
        response = self.client.get(self.view_cart_url)

        # Проверяем, что элементы корзины отображаются
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test_file1.pdf")
        self.assertContains(response, "test_file2.pdf")

        # Проверяем, что переданные элементы корзины корректны
        cart_items = response.context["cart_items"]
        self.assertEqual(cart_items.count(), 2)
        self.assertIn(self.cart_item1, cart_items)
        self.assertIn(self.cart_item2, cart_items)

    def test_total_price_calculation(self):
        response = self.client.get(self.view_cart_url)

        # Проверяем, что общая стоимость корзины рассчитана корректно
        total_price = response.context["total_price"]
        self.assertEqual(total_price, 125.0)  # 50.0 + 75.0

    def test_empty_cart(self):
        # Удаляем все элементы корзины
        Cart.objects.all().delete()

        response = self.client.get(self.view_cart_url)

        # Проверяем, что корзина отображается как пустая
        cart_items = response.context["cart_items"]
        self.assertEqual(cart_items.count(), 0)
        self.assertContains(response, "Корзина пуста")  # Зависит от шаблона
