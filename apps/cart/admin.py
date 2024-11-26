from django.contrib import admin

from apps.cart.models import Cart


@admin.action(description="Отметить как оплаченные")
def mark_as_paid(queryset):
    queryset.update(payment=True)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """
    Админка для модели Cart.
    """

    # Поля, отображаемые в списке заказов
    list_display = ("id", "user", "docs", "order_price", "payment")
    list_filter = ("payment",)
    search_fields = (
        "user__username",
        "docs__name",
    )  # Поиск по имени пользователя и документа
    ordering = ("id",)

    # Поля для редактирования
    fields = ("user", "docs", "order_price", "payment")
    readonly_fields = ("order_price",)
    actions = [mark_as_paid]

    # Добавление кастомного отображения для связанных объектов
    @admin.display(description="Документ")
    def document_name(self, obj):
        return obj.docs.name if obj.docs else "Документ отсутствует"

    @admin.display(description="Пользователь")
    def user_name(self, obj):
        return obj.user.username if obj.user else "Не задан"
