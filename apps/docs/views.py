import os

import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from dotenv.main import load_dotenv

from apps.cart.models import Cart
from config import settings

from .models import Docs, UserToDocs

load_dotenv()

FASTAPI_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8000")


@login_required
def main_page(request):
    # Получаем все документы текущего пользователя через UserToDocs
    user_docs = (
        UserToDocs.objects.filter(user=request.user)
        .select_related("doc")
        .order_by("-id")
    )
    documents = [user_doc.doc for user_doc in user_docs]

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


@login_required
def upload_photos(request):
    if request.method == "POST":
        files = request.FILES.getlist("files")
        error = None
        for file in files:
            # Проверка формата и размера
            if not file.name.lower().endswith(("jpg", "jpeg", "png", "pdf")):
                error = "Неправильный формат файла."
            elif file.size > 5 * 1024 * 1024:  # 5MB
                error = "Файл слишком большой."
            else:
                url = f"{FASTAPI_URL}/upload_doc"
                try:
                    with file.open("rb") as f:
                        response = requests.post(url, files={"file": f})
                        if response.status_code == 200:

                            # Сохранение файла
                            doc = Docs.objects.create(
                                user=request.user, file=file, size=file.size // 1024
                            )
                            # Создание записи в UserToDocs
                            UserToDocs.objects.create(user=request.user, doc=doc)
                except requests.exceptions.RequestException:
                    messages.warning(request, "Произошла ошибка при загрузке файла.")

        if error:
            return render(request, "upload/upload.html", {"error": error})
        return redirect("main")

    return render(request, "upload/upload.html")


@login_required
def analyze_file(request, doc_id):
    # Получение документа
    doc = get_object_or_404(Docs, id=doc_id, user=request.user)

    # Логика определения статуса
    if not doc.payment_status:
        messages.warning(request, "Для анализа документа необходимо произвести оплату.")
        return redirect("main")

    # Обработка POST-запроса
    if request.method == "POST":
        if not doc.analysis_done:
            # Отправка документа на анализ через FastAPI
            url = f"{FASTAPI_URL}/doc_analyse"
            params = {"document_id": doc_id}
            try:
                response = requests.post(url, params=params)
                if response.status_code == 200:
                    # Помечаем документ как проанализированный
                    doc.analysis_done = True
                    doc.save()
                    messages.success(
                        request, f"Документ {doc.id} успешно проанализирован."
                    )
                else:
                    error_message = response.json().get(
                        "message", "Неизвестная ошибка."
                    )
                    messages.error(
                        request,
                        f"Ошибка отправки документа на анализ через FastAPI: {error_message}",
                    )
            except requests.RequestException as e:
                messages.error(request, f"Ошибка соединения с FastAPI: {e}")
        else:
            messages.info(request, f"Документ {doc.id} уже был проанализирован.")
        return redirect("main")

    # Отображение страницы анализа
    return redirect("main")


@login_required
def confirm_payment(request, doc_id):
    doc = get_object_or_404(Docs, id=doc_id, user=request.user)
    doc.payment_status = True
    doc.save()

    # Удаляем документ из корзины, если он там есть
    Cart.objects.filter(user=request.user, docs=doc).delete()

    messages.success(request, "Оплата успешно выполнена!")
    return redirect("main")


@login_required
def confirm_all_payments(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(
            ["POST"]
        )  # Возвращает 405 для методов, кроме POST

    cart_items = Cart.objects.filter(user=request.user, payment=False)

    # Помечаем все элементы корзины как оплаченные и обновляем статус документов
    for item in cart_items:
        item.payment = True
        item.save()

        # Обновляем статус оплаты документа
        doc = item.docs
        doc.payment_status = True
        doc.save()

    messages.success(request, "Оплата успешно выполнена!")
    return redirect("view_cart")


@login_required
def get_text(request, doc_id):
    # Получаем объект документа
    doc = get_object_or_404(Docs, id=doc_id, user=request.user)

    # URL FastAPI сервиса
    url = f"{FASTAPI_URL}/get_text/{doc_id}"

    # Выполняем запрос к FastAPI
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        text = data.get("text", "Текст недоступен.")
        # Сохраняем текст в базе данных
        doc.text = text
        doc.save()
    else:
        text = "Не удалось получить текст из FastAPI."

    # Передаем текст в шаблон
    return render(request, "docs/get_text.html", {"doc": doc, "text": text})


@login_required
def delete_file(request, doc_id):
    if request.method == "POST":
        # Получаем объект документа
        doc = get_object_or_404(Docs, id=doc_id)

        # Проверяем, может ли пользователь удалить этот файл
        if request.user != doc.user and not request.user.is_staff:
            return HttpResponseForbidden("Вы не можете удалить этот файл.")

        # Подключаемся к FastAPI
        url = f"{FASTAPI_URL}/delete_doc"
        response = requests.delete(url, params={"document_id": doc_id})
        if response.status_code == 200:

            # Удаляем файл из локальной файловой системы
            file_path = os.path.join(settings.MEDIA_ROOT, doc.file.name)
            if os.path.exists(file_path):
                os.remove(file_path)

            # Удаляем запись из таблицы UserToDocs
            UserToDocs.objects.filter(doc=doc).delete()

            # Удаляем запись из базы данных
            doc.delete()

        # Перенаправляем на главную страницу
    return redirect("main")


@login_required
def add_to_cart(request, doc_id):
    if request.method == "POST":
        doc = get_object_or_404(Docs, id=doc_id, user=request.user)

        if doc.payment_status:
            messages.warning(request, "Этот документ уже оплачен.")
            return redirect("main")

        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            docs=doc,
        )

        if created:
            cart_item.calculate_price()

        messages.success(request, "Документ добавлен в корзину.")
        return redirect("main")


@login_required
def remove_from_cart(request, doc_id):
    if request.method == "POST":
        cart_item = get_object_or_404(Cart, user=request.user, docs_id=doc_id)
        cart_item.delete()
        messages.success(request, "Документ удален из корзины.")
        return redirect("main")


@login_required
def view_cart(request):
    # Получаем только неоплаченные элементы корзины текущего пользователя
    cart_items = Cart.objects.filter(user=request.user, payment=False)
    total_price = sum(item.order_price for item in cart_items)
    return render(
        request,
        "cart/cart.html",
        {
            "cart_items": cart_items,
            "total_price": total_price,
        },
    )
