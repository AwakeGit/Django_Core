# from django.contrib.auth.models import User
# from django.test import Client, TestCase
# from django.urls import reverse
#
# from apps.cart.models import Cart
# from apps.docs.models import Docs, UserToDocs
#
#
# class MainPageTest(TestCase):
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
#         # Создаем документы для тестового пользователя
#         self.docs = [
#             Docs.objects.create(
#                 user=self.user, file=f"test_file_{i}.pdf", size=100 * (i + 1)
#             )
#             for i in range(5)
#         ]
#
#         # Связываем документы с пользователем через UserToDocs
#         for doc in self.docs:
#             UserToDocs.objects.create(user=self.user, doc=doc)
#
#         # Добавляем документ в корзину
#         self.cart_item = Cart.objects.create(user=self.user, docs=self.docs[0])
#
#     def test_main_page_pagination(self):
#         # Проверяем первую страницу
#         response = self.client.get(reverse("main"))
#         self.assertEqual(response.status_code, 200)
#
#         # Убедимся, что пагинация работает
#         self.assertIn("page_obj", response.context)
#         self.assertEqual(
#             len(response.context["page_obj"]), 3
#         )  # Показано 3 документа на странице
#
#     def test_main_page_documents(self):
#         response = self.client.get(reverse("main"))
#         self.assertEqual(response.status_code, 200)
#
#         # Проверяем, что все документы отображаются в порядке убывания ID
#         page_obj = response.context["page_obj"]
#         expected_docs = list(UserToDocs.objects.filter(user=self.user).order_by("-id"))
#         self.assertEqual(
#             list(page_obj.object_list), [user_doc.doc for user_doc in expected_docs[:3]]
#         )
#
#     def test_cart_items(self):
#         response = self.client.get(reverse("main"))
#         self.assertEqual(response.status_code, 200)
#
#         # Проверяем, что документы в корзине отображаются
#         cart_docs_ids = response.context["cart_docs_ids"]
#         self.assertIn(self.cart_item.docs.id, cart_docs_ids)
#
#     def test_access_for_anonymous_user(self):
#         # Разлогиним пользователя
#         self.client.logout()
#         response = self.client.get(reverse("main"))
#
#         # Убедимся, что анонимного пользователя перенаправляет на страницу входа
#         self.assertEqual(response.status_code, 302)
#         self.assertIn("/login/", response.url)
