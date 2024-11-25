from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from apps.cart.models import Cart
from apps.docs.models import Docs


class RemoveFromCartTest(TestCase):
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
        self.doc = Docs.objects.create(user=self.user, file="test_file.pdf", size=100)

        # Добавляем документ в корзину
        self.cart_item = Cart.objects.create(user=self.user, docs=self.doc)

        # URL для удаления документа из корзины
        self.remove_from_cart_url = reverse(
            "remove_from_cart", kwargs={"doc_id": self.doc.id}
        )

    def test_unauthenticated_access(self):
        # Разлогиниваем пользователя
        self.client.logout()

        response = self.client.post(self.remove_from_cart_url)

        # Проверяем, что неавторизованный пользователь перенаправляется на страницу входа
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_nonexistent_cart_item(self):
        # Попытка удаления несуществующего элемента корзины
        nonexistent_url = reverse("remove_from_cart", kwargs={"doc_id": 999})

        response = self.client.post(nonexistent_url)

        # Проверяем, что возвращается 404 ошибка
        self.assertEqual(response.status_code, 404)

    def test_successful_removal_from_cart(self):
        response = self.client.post(self.remove_from_cart_url, follow=True)

        # Проверяем, что документ был удален из корзины
        self.assertFalse(Cart.objects.filter(user=self.user, docs=self.doc).exists())

        # Проверяем сообщение об успешном удалении
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Документ удален из корзины.")
