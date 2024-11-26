# apps/docs/views.py

import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.views import View

from apps.cart.models import Cart
from apps.docs.exceptions import ServiceError
from apps.docs.services.docs_service import DocService

logger = logging.getLogger("docs")


class MainPageView(LoginRequiredMixin, View):
    """Представление для главной страницы."""

    def get(self, request):
        """
        Отображает главную страницу с документами пользователя.

        :param request: HttpRequest
        :return: HttpResponse с главной страницей
        """
        logger.info("GET-запрос на главную страницу.")
        documents = DocService.get_user_documents(request.user)

        cart_items = Cart.objects.filter(user=request.user)
        cart_docs_ids = cart_items.values_list("docs_id", flat=True)

        paginator = Paginator(documents, 3)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return render(
            request,
            "main/main.html",
            {
                "page_obj": page_obj,
                "cart_docs_ids": cart_docs_ids,
            },
        )


class UploadPhotosView(LoginRequiredMixin, View):
    """Представление для загрузки файлов."""

    def get(self, request):
        """
        Отображает форму загрузки файлов.

        :param request: HttpRequest
        :return: HttpResponse с формой загрузки
        """
        logger.info("GET-запрос на страницу загрузки файлов.")
        return render(request, "upload/upload.html")

    def post(self, request):
        """
        Обрабатывает загрузку файлов.

        :param request: HttpRequest
        :return: Перенаправление на главную страницу или повторная загрузка формы с ошибками
        """
        logger.info("POST-запрос для загрузки файлов.")
        files = request.FILES.getlist("files")
        try:
            DocService.upload_files(request.user, files)
            messages.success(request, "Файлы успешно загружены.")
            return redirect("main")
        except ServiceError as e:
            logger.error(f"Ошибка при загрузке файлов: {e.message}")
            messages.error(request, e.message)
            return render(request, "upload/upload.html", {"error": e.message})
        except Exception:
            logger.exception("Неожиданная ошибка при загрузке файлов.")
            messages.error(request, "Произошла ошибка при загрузке файлов.")
            return render(
                request,
                "upload/upload.html",
                {"error": "Произошла ошибка при загрузке файлов."},
            )


class AnalyzeFileView(LoginRequiredMixin, View):
    """Представление для анализа файлов."""

    def post(self, request, doc_id):
        """
        Обрабатывает запрос на анализ документа.

        :param request: HttpRequest
        :param doc_id: ID документа
        :return: Перенаправление на главную страницу
        """
        logger.info(f"POST-запрос на анализ документа {doc_id}.")
        try:
            DocService.analyze_document(request.user, doc_id)
            messages.success(request, f"Документ {doc_id} успешно проанализирован.")
        except ServiceError as e:
            logger.error(f"Ошибка при анализе документа {doc_id}: {e.message}")
            messages.error(request, e.message)
        except Exception:
            logger.exception(f"Неожиданная ошибка при анализе документа {doc_id}.")
            messages.error(request, "Произошла ошибка при анализе документа.")
        return redirect("main")


class GetTextView(LoginRequiredMixin, View):
    """Представление для получения текста документа."""

    def get(self, request, doc_id):
        """
        Отображает текст документа.

        :param request: HttpRequest
        :param doc_id: ID документа
        :return: HttpResponse с текстом документа
        """
        logger.info(f"GET-запрос на получение текста документа {doc_id}.")
        try:
            text = DocService.get_document_text(request.user, doc_id)
            return render(request, "docs/get_text.html", {"text": text})
        except ServiceError as e:
            logger.error(f"Ошибка при получении текста документа {doc_id}: {e.message}")
            messages.error(request, e.message)
            return redirect("main")
        except Exception:
            logger.exception(
                f"Неожиданная ошибка при получении текста документа {doc_id}."
            )
            messages.error(request, "Произошла ошибка при получении текста документа.")
            return redirect("main")


class DeleteFileView(LoginRequiredMixin, View):
    """Представление для удаления файлов."""

    def post(self, request, doc_id):
        """
        Обрабатывает запрос на удаление документа.

        :param request: HttpRequest
        :param doc_id: ID документа
        :return: Перенаправление на главную страницу
        """
        logger.info(f"POST-запрос на удаление документа {doc_id}.")
        try:
            DocService.delete_document(request.user, doc_id)
            messages.success(request, f"Документ {doc_id} успешно удален.")
        except ServiceError as e:
            logger.error(f"Ошибка при удалении документа {doc_id}: {e.message}")
            messages.error(request, e.message)
        except Exception:
            logger.exception(f"Неожиданная ошибка при удалении документа {doc_id}.")
            messages.error(request, "Произошла ошибка при удалении документа.")
        return redirect("main")
