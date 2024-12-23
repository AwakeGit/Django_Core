# import os
# from unittest import mock
#
# from django.conf import settings
# from django.contrib.auth.models import User
# from django.test import Client, TestCase
# from django.urls import reverse
#
# from apps.docs.models import Docs, UserToDocs
#
#
# class DeleteFileTest(TestCase):
#     def setUp(self):
#         # Создаем тестового пользователя и авторизуем его
#         self.client = Client()
#         self.username = "testuser"
#         self.password = "testpassword"
#         self.user = User.objects.create_user(
#             username=self.username, password=self.password
#         )
#         self.client.login(username=self.username, password=self.password)
#
#         # Создаем документ
#         self.doc = Docs.objects.create(user=self.user, file="test_file.pdf", size=100)
#
#         # Связываем документ с пользователем через UserToDocs
#         UserToDocs.objects.create(user=self.user, doc=self.doc)
#
#         # URL для удаления документа
#         self.delete_file_url = reverse("delete_file", kwargs={"doc_id": self.doc.id})
#
#         # Создаем тестовый файл
#         self.file_path = os.path.join(settings.MEDIA_ROOT, self.doc.file.name)
#         os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
#         with open(self.file_path, "w") as f:
#             f.write("Test content")
#
#     def tearDown(self):
#         # Удаляем тестовый файл, если он существует
#         if os.path.exists(self.file_path):
#             os.remove(self.file_path)
#
#     def test_unauthenticated_access(self):
#         # Разлогиниваем пользователя
#         self.client.logout()
#
#         response = self.client.post(self.delete_file_url)
#
#         # Проверяем, что неавторизованный пользователь перенаправляется на страницу входа
#         self.assertEqual(response.status_code, 302)
#         self.assertIn("/login/", response.url)
#
#     def test_nonexistent_document(self):
#         # Попытка удаления несуществующего документа
#         nonexistent_url = reverse("delete_file", kwargs={"doc_id": 999})
#
#         response = self.client.post(nonexistent_url)
#
#         # Проверяем, что возвращается 404 ошибка
#         self.assertEqual(response.status_code, 404)
#
#     def test_forbidden_access(self):
#         # Создаем другого пользователя
#         User.objects.create_user(username="otheruser", password="otherpassword")
#
#         # Логинимся под другим пользователем
#         self.client.logout()
#         self.client.login(username="otheruser", password="otherpassword")
#
#         response = self.client.post(self.delete_file_url)
#
#         # Проверяем, что доступ запрещен
#         self.assertEqual(response.status_code, 403)
#
#     @mock.patch("requests.delete")
#     def test_successful_file_deletion(self, mock_delete):
#         # Мокаем успешный ответ от FastAPI
#         mock_response = mock.Mock()
#         mock_response.status_code = 200
#         mock_delete.return_value = mock_response
#
#         response = self.client.post(self.delete_file_url)
#
#         # Проверяем, что документ был удален из базы данных
#         self.assertFalse(Docs.objects.filter(id=self.doc.id).exists())
#
#         # Проверяем, что файл удален из файловой системы
#         self.assertFalse(os.path.exists(self.file_path))
#
#         # Проверяем, что пользователь-документ связь удалена
#         self.assertFalse(UserToDocs.objects.filter(doc=self.doc).exists())
#
#         # Проверяем перенаправление на главную страницу
#         self.assertEqual(response.status_code, 302)
#         self.assertEqual(response.url, reverse("main"))
#
#     @mock.patch("requests.delete")
#     def test_failed_fastapi_deletion(self, mock_delete):
#         # Мокаем ошибочный ответ от FastAPI
#         mock_response = mock.Mock()
#         mock_response.status_code = 500
#         mock_delete.return_value = mock_response
#
#         self.client.post(self.delete_file_url)
#
#         # Проверяем, что документ не был удален из базы данных
#         self.assertTrue(Docs.objects.filter(id=self.doc.id).exists())
#
#         # Проверяем, что файл остался в файловой системе
#         self.assertTrue(os.path.exists(self.file_path))
