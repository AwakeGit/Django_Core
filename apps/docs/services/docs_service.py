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
        """
        user_docs = (
            UserToDocs.objects.filter(user=user).select_related("doc").order_by("-id")
        )
        return [user_doc.doc for user_doc in user_docs]

    @staticmethod
    def upload_files(user, files, auth_token):
        """
        Загружает файлы через DRF-прокси, который проверит токен и проксирует их на FastAPI.
        """
        upload_url = f"{settings.DRF_PROXY_URL}api/v1/docs/"
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }
        logger.info(f"Отправка файла в DRF-прокси: {upload_url}, заголовки: {headers}")

        for file in files:
            if not file.name.lower().endswith(("jpg", "jpeg", "png", "pdf")):
                raise ServiceError("Неправильный формат файла.")
            elif file.size > 5 * 1024 * 1024:
                raise ServiceError("Файл слишком большой.")

            try:
                content = file.read()
                file.seek(0)

                response = requests.post(
                    upload_url,
                    headers=headers,
                    files={"file": (file.name, content)},
                )
                logger.info(
                    f"Ответ от DRF-прокси: статус={response.status_code}, тело={response.text}"
                )

                if response.status_code == 201:
                    data = response.json()
                    fastapi_doc_id = data.get("id")
                    if not fastapi_doc_id:
                        raise ServiceError(
                            "Не удалось получить идентификатор документа из DRF-прокси."
                        )

                    # Сохраняем документ с fastapi_id
                    doc = Docs.objects.create(
                        user=user,
                        file=file,
                        size=file.size // 1024,
                        fastapi_id=fastapi_doc_id,
                    )
                    UserToDocs.objects.create(user=user, doc=doc)
                else:
                    error_message = response.json().get(
                        "message", "Неизвестная ошибка."
                    )
                    raise ServiceError(f"Ошибка загрузки файла: {error_message}")

            except requests.RequestException as e:
                logger.error(f"Ошибка при соединении с DRF-прокси: {e}")
                raise ServiceError("Ошибка при соединении с сервисом загрузки.")

    @staticmethod
    def analyze_document(user, doc_id, auth_token):
        """
        Анализирует документ через FastAPI.
        """
        doc = get_object_or_404(Docs, id=doc_id, user=user)

        if not doc.payment_status:
            raise ServiceError("Для анализа документа необходимо произвести оплату.")

        if doc.analysis_done:
            raise ServiceError(f"Документ {doc.id} уже был проанализирован.")

        analyze_url = f"{settings.DRF_PROXY_URL}api/v1/docs/{doc.fastapi_id}/analyze/"
        logger.info(analyze_url)
        headers = {
            "Authorization": f"Bearer {auth_token}",
        }
        response = requests.post(analyze_url, headers=headers)
        try:
            if response.status_code in (200, 201):
                doc.analysis_done = True
                doc.save()
            else:
                error_message = response.json().get("message", "Неизвестная ошибка.")
                raise ServiceError(f"Ошибка анализа документа: {error_message}")

        except requests.RequestException as e:
            logger.error(f"Ошибка при соединении с DRF-прокси: {e}")
            raise ServiceError("Ошибка при соединении с DRF-прокси.")

    @staticmethod
    def get_document_text(user, doc_id, auth_token):
        """
        Получает текст документа через FastAPI.
        """
        doc = get_object_or_404(Docs, id=doc_id, user=user)
        url = f"{settings.DRF_PROXY_URL}api/v1/docs/{doc_id}/text/"
        logger.info(f"Запрос на получение текста: {url}")

        headers = {"Authorization": f"Bearer {auth_token}"}

        try:
            response = requests.get(url, headers=headers)
            logger.info(
                f"Ответ от FastAPI: статус={response.status_code}, тело={response.text}"
            )
            if response.status_code == 200:
                data = response.json()
                text = data.get("text", "Текст недоступен.")
                doc.text = text
                doc.save()
                return text
            else:
                error_message = response.json().get("message", "Неизвестная ошибка.")
                raise ServiceError(f"Ошибка получения текста: {error_message}")
        except requests.RequestException as e:
            logger.error(f"Ошибка соединения с FastAPI: {e}")
            raise ServiceError("Ошибка соединения с FastAPI.")

    @staticmethod
    def delete_document(user, doc_id, auth_token):
        """
        Удаляет документ и связанные с ним данные.
        """
        doc = get_object_or_404(Docs, id=doc_id)
        if user != doc.user and not user.is_staff:
            raise ServiceError("Вы не можете удалить этот файл.")

        url = f"{settings.DRF_PROXY_URL}api/v1/docs/<doc_id>/"

        headers = {
            "Authorization": f"Bearer {auth_token}",
        }
        logger.info(f"Запрос на удаление: {url}")

        try:
            response = requests.delete(url, headers=headers)
            logger.info(
                f"Ответ от FastAPI на удаление: статус={response.status_code}, тело={response.text}"
            )
            if response.status_code in [200, 204]:
                file_path = os.path.join(settings.MEDIA_ROOT, doc.file.name)
                if os.path.exists(file_path):
                    os.remove(file_path)

                UserToDocs.objects.filter(doc=doc).delete()
                doc.delete()

                logger.info(f"Документ {doc.id} успешно удалён.")
            else:
                error_message = response.json().get("message", "Неизвестная ошибка.")
                raise ServiceError(f"Ошибка удаления документа: {error_message}")

        except requests.RequestException as e:
            logger.error(f"Ошибка соединения с FastAPI: {e}")
            raise ServiceError("Ошибка соединения с FastAPI.")
