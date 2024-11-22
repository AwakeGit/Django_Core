import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from apps.cart.models import Cart
from config import settings

from .models import Docs


@login_required
def main_page(request):
    # Получаем все документы текущего пользователя
    documents = Docs.objects.filter(user=request.user).order_by("-id")
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
    print("upload_photos")
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
                # Сохранение файла
                Docs.objects.create(
                    user=request.user, file=file, size=file.size // 1024
                )
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
            doc.analysis_done = True
            doc.save()
            messages.success(request, f"Документ {doc.id} успешно проанализирован.")
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
    if request.method == "POST":
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
    doc = get_object_or_404(Docs, id=doc_id, user=request.user)
    text = doc.text if doc.text else "Текст недоступен или еще не проанализирован."
    return render(request, "docs/get_text.html", {"doc": doc, "text": text})


@login_required
def delete_file(request, doc_id):
    if request.method == "POST":
        # Получаем объект документа
        doc = get_object_or_404(Docs, id=doc_id)

        # Проверяем, может ли пользователь удалить этот файл
        if request.user != doc.user and not request.user.is_staff:
            return HttpResponseForbidden("Вы не можете удалить этот файл.")

        # Удаляем файл из локальной файловой системы
        file_path = os.path.join(settings.MEDIA_ROOT, doc.file.name)
        if os.path.exists(file_path):
            os.remove(file_path)

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

        Cart.objects.get_or_create(
            user=request.user,
            docs=doc,
            defaults={"order_price": doc.size * 0.1},  # Пример расчета цены
        )

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
