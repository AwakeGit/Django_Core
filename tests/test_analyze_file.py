from unittest import mock

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from apps.docs.models import Docs


class AnalyzeFileTest(TestCase):
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
            user=self.user,
            file="test_file.pdf",
            size=100,
            payment_status=False,
            analysis_done=False,
        )

        # URL для теста
        self.analyze_url = reverse("analyze_file", kwargs={"doc_id": self.doc.id})

    def test_unauthenticated_access(self):
        # Разлогиним пользователя
        self.client.logout()

        response = self.client.get(self.analyze_url)

        # Убедимся, что неавторизованного пользователя перенаправляют на страницу входа
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_nonexistent_document(self):
        # Попытка доступа к несуществующему документу
        nonexistent_url = reverse("analyze_file", kwargs={"doc_id": 999})

        response = self.client.get(nonexistent_url)

        # Убедимся, что возвращается 404
        self.assertEqual(response.status_code, 404)

    def test_document_requires_payment(self):
        # Попытка анализа документа без оплаты
        response = self.client.post(self.analyze_url, follow=True)

        # Проверяем сообщение о необходимости оплаты
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), "Для анализа документа необходимо произвести оплату."
        )
        self.doc.refresh_from_db()
        self.assertFalse(self.doc.analysis_done)

    @mock.patch("requests.post")
    def test_successful_analysis(self, mock_post):
        # Мокаем успешный ответ от FastAPI
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Обновляем статус оплаты документа
        self.doc.payment_status = True
        self.doc.save()

        response = self.client.post(self.analyze_url, follow=True)

        # Проверяем успешное сообщение
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertIn(
            f"Документ {self.doc.id} успешно проанализирован.", str(messages[0])
        )
        self.doc.refresh_from_db()
        self.assertTrue(self.doc.analysis_done)

    @mock.patch("requests.post")
    def test_failed_fastapi_analysis(self, mock_post):
        # Мокаем ошибочный ответ от FastAPI
        mock_response = mock.Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Ошибка анализа"}
        mock_post.return_value = mock_response

        # Обновляем статус оплаты документа
        self.doc.payment_status = True
        self.doc.save()

        response = self.client.post(self.analyze_url, follow=True)

        # Проверяем сообщение об ошибке
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertIn(
            "Ошибка отправки документа на анализ через FastAPI: Ошибка анализа",
            str(messages[0]),
        )
        self.doc.refresh_from_db()
        self.assertFalse(self.doc.analysis_done)

    @mock.patch("requests.post")
    def test_analysis_done_message(self, mock_post):
        # Устанавливаем статус документа как проанализированный
        self.doc.payment_status = True
        self.doc.analysis_done = True
        self.doc.save()

        response = self.client.post(self.analyze_url, follow=True)

        # Проверяем, что отображается сообщение о том, что документ уже проанализирован
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertIn(
            f"Документ {self.doc.id} уже был проанализирован.", str(messages[0])
        )
