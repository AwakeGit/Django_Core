from unittest import mock

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from apps.docs.models import Docs


class GetTextTest(TestCase):
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

        # URL для получения текста
        self.get_text_url = reverse("get_text", kwargs={"doc_id": self.doc.id})

    def test_unauthenticated_access(self):
        # Разлогиниваем пользователя
        self.client.logout()

        response = self.client.get(self.get_text_url)

        # Проверяем, что неавторизованного пользователя перенаправляют на страницу входа
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_nonexistent_document(self):
        # Попытка доступа к несуществующему документу
        nonexistent_url = reverse("get_text", kwargs={"doc_id": 999})

        response = self.client.get(nonexistent_url)

        # Проверяем, что возвращается 404 ошибка
        self.assertEqual(response.status_code, 404)

    @mock.patch("requests.get")
    def test_successful_text_retrieval(self, mock_get):
        # Мокаем успешный ответ от FastAPI
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"text": "Это тестовый текст."}
        mock_get.return_value = mock_response

        response = self.client.get(self.get_text_url)

        # Проверяем, что текст передается в шаблон
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Это тестовый текст.")

        # Проверяем, что текст сохраняется в базе данных
        self.doc.refresh_from_db()
        self.assertEqual(self.doc.text, "Это тестовый текст.")

    @mock.patch("requests.get")
    def test_failed_text_retrieval(self, mock_get):
        # Мокаем ошибочный ответ от FastAPI
        mock_response = mock.Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        response = self.client.get(self.get_text_url)

        # Проверяем, что отображается сообщение об ошибке
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Не удалось получить текст из FastAPI.")

        # Проверяем, что текст в базе данных остался неизменным
        self.doc.refresh_from_db()
        self.assertIsNone(self.doc.text)  # Убедимся, что текст не обновлялся
