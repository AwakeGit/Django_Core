# apps/docs/services.py

import logging
import os

import requests
from django.conf import settings
from django.shortcuts import get_object_or_404

from apps.docs.exceptions import ServiceError
from apps.docs.models import Docs, UserToDocs

logger = logging.getLogger("docs")


class DocService:
    """Сервис для работы с документами."""

    FASTAPI_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8000")

    @staticmethod
    def get_user_documents(user):
        """
        Получает документы пользователя.

        :param user: Пользователь
        :return: Список документов
        """
        user_docs = (
            UserToDocs.objects.filter(user=user).select_related("doc").order_by("-id")
        )
        documents = [user_doc.doc for user_doc in user_docs]
        return documents

    @staticmethod
    def upload_files(user, files):
        """
        Загружает файлы на FastAPI и сохраняет их в базе данных.

        :param user: Пользователь, который загружает файлы
        :param files: Список файлов
        :raises ServiceError: Если произошла ошибка при загрузке
        """
        for file in files:
            # Проверка формата и размера
            if not file.name.lower().endswith(("jpg", "jpeg", "png", "pdf")):
                raise ServiceError("Неправильный формат файла.")
            elif file.size > 5 * 1024 * 1024:  # 5MB
                raise ServiceError("Файл слишком большой.")
            else:
                url = f"{DocService.FASTAPI_URL}/upload_doc"
                try:
                    with file.open("rb") as f:
                        response = requests.post(url, files={"file": f})
                        if response.status_code == 200:
                            # Сохранение файла в базе данных
                            doc = Docs.objects.create(
                                user=user, file=file, size=file.size // 1024
                            )
                            # Создание записи в UserToDocs
                            UserToDocs.objects.create(user=user, doc=doc)
                        else:
                            error_message = response.json().get(
                                "message", "Неизвестная ошибка."
                            )
                            raise ServiceError(
                                f"Ошибка загрузки файла: {error_message}"
                            )
                except requests.exceptions.RequestException as e:
                    logger.error(f"Ошибка при соединении с FastAPI: {e}")
                    raise ServiceError("Ошибка при соединении с сервисом загрузки.")

    @staticmethod
    def analyze_document(user, doc_id):
        """
        Анализирует документ через FastAPI.

        :param user: Пользователь, который запрашивает анализ
        :param doc_id: ID документа
        :raises ServiceError: Если произошла ошибка при анализе
        """
        doc = get_object_or_404(Docs, id=doc_id, user=user)

        if not doc.payment_status:
            raise ServiceError("Для анализа документа необходимо произвести оплату.")

        if doc.analysis_done:
            raise ServiceError(f"Документ {doc.id} уже был проанализирован.")

        url = f"{DocService.FASTAPI_URL}/doc_analyse"
        params = {"document_id": doc_id}
        try:
            response = requests.post(url, params=params)
            if response.status_code == 200:
                doc.analysis_done = True
                doc.save()
                logger.info(f"Документ {doc.id} успешно проанализирован.")
            else:
                error_message = response.json().get("message", "Неизвестная ошибка.")
                raise ServiceError(f"Ошибка анализа документа: {error_message}")
        except requests.RequestException as e:
            logger.error(f"Ошибка соединения с FastAPI: {e}")
            raise ServiceError(f"Ошибка соединения с FastAPI: {e}")

    @staticmethod
    def get_document_text(user, doc_id):
        """
        Получает текст документа через FastAPI.

        :param user: Пользователь, который запрашивает текст
        :param doc_id: ID документа
        :return: Текст документа
        :raises ServiceError: Если произошла ошибка при получении текста
        """
        doc = get_object_or_404(Docs, id=doc_id, user=user)
        url = f"{DocService.FASTAPI_URL}/get_text/{doc_id}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                text = data.get("text", "Текст недоступен.")
                # Сохраняем текст в базе данных
                doc.text = text
                doc.save()
                return text
            else:
                error_message = response.json().get("message", "Неизвестная ошибка.")
                raise ServiceError(f"Ошибка получения текста: {error_message}")
        except requests.RequestException as e:
            logger.error(f"Ошибка соединения с FastAPI: {e}")
            raise ServiceError(f"Ошибка соединения с FastAPI: {e}")

    @staticmethod
    def delete_document(user, doc_id):
        """
        Удаляет документ и связанные с ним данные.

        :param user: Пользователь, который запрашивает удаление
        :param doc_id: ID документа
        :raises ServiceError: Если произошла ошибка при удалении
        """
        doc = get_object_or_404(Docs, id=doc_id)

        if user != doc.user and not user.is_staff:
            raise ServiceError("Вы не можете удалить этот файл.")

        url = f"{DocService.FASTAPI_URL}/delete_doc"
        try:
            response = requests.delete(url, params={"document_id": doc_id})
            if response.status_code == 200:
                # Удаляем файл из локальной файловой системы
                file_path = os.path.join(settings.MEDIA_ROOT, doc.file.name)
                if os.path.exists(file_path):
                    os.remove(file_path)

                # Удаляем записи из базы данных
                UserToDocs.objects.filter(doc=doc).delete()
                doc.delete()
                logger.info(f"Документ {doc.id} успешно удален.")
            else:
                error_message = response.json().get("message", "Неизвестная ошибка.")
                raise ServiceError(f"Ошибка удаления документа: {error_message}")
        except requests.RequestException as e:
            logger.error(f"Ошибка соединения с FastAPI: {e}")
            raise ServiceError(f"Ошибка соединения с FastAPI: {e}")
