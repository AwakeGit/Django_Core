from unittest import mock

import requests
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from apps.docs.models import Docs, UserToDocs


class UploadPhotosTest(TestCase):
    def setUp(self):
        # Создаем тестового пользователя и авторизуем его
        self.client = Client()
        self.username = "testuser"
        self.password = "testpass"
        self.user = User.objects.create_user(
            username=self.username, password=self.password
        )
        self.client.login(username=self.username, password=self.password)
        self.upload_url = reverse("upload_photos")  # Убедитесь, что имя URL совпадает

    @mock.patch("requests.post")
    def test_upload_valid_file(self, mock_post):
        # Мокаем ответ от requests.post
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Создаем валидный файл
        file_content = b"This is a test file"
        uploaded_file = SimpleUploadedFile(
            "test.jpg", file_content, content_type="image/jpeg"
        )

        response = self.client.post(self.upload_url, {"files": [uploaded_file]})

        # Проверяем успешную загрузку файла
        self.assertRedirects(response, reverse("main"))
        self.assertEqual(Docs.objects.count(), 1)
        self.assertEqual(UserToDocs.objects.count(), 1)

    def test_upload_invalid_format_file(self):
        # Создаем файл с недопустимым форматом
        file_content = b"This is a test file"
        uploaded_file = SimpleUploadedFile(
            "test.txt", file_content, content_type="text/plain"
        )

        response = self.client.post(self.upload_url, {"files": [uploaded_file]})

        # Проверяем отображение ошибки
        self.assertTemplateUsed(response, "upload/upload.html")
        self.assertContains(response, "Неправильный формат файла.")
        self.assertEqual(Docs.objects.count(), 0)
        self.assertEqual(UserToDocs.objects.count(), 0)

    def test_upload_large_file(self):
        # Создаем файл размером более 5MB
        file_content = b"A" * (5 * 1024 * 1024 + 1)  # 5MB + 1 байт
        uploaded_file = SimpleUploadedFile(
            "large.jpg", file_content, content_type="image/jpeg"
        )

        response = self.client.post(self.upload_url, {"files": [uploaded_file]})

        # Проверяем отображение ошибки
        self.assertTemplateUsed(response, "upload/upload.html")
        self.assertContains(response, "Файл слишком большой.")
        self.assertEqual(Docs.objects.count(), 0)
        self.assertEqual(UserToDocs.objects.count(), 0)

    @mock.patch("requests.post")
    def test_upload_requests_exception(self, mock_post):
        mock_post.side_effect = requests.exceptions.RequestException

        file_content = b"This is a test file"
        uploaded_file = SimpleUploadedFile(
            "test.jpg", file_content, content_type="image/jpeg"
        )

        response = self.client.post(
            self.upload_url, {"files": [uploaded_file]}, follow=True
        )

        # Проверяем наличие сообщения через get_messages
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Произошла ошибка при загрузке файла.")
        self.assertEqual(Docs.objects.count(), 0)
        self.assertEqual(UserToDocs.objects.count(), 0)
