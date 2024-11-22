from django.urls import path

from . import views

urlpatterns = [
    path("", views.main_page, name="main"),
    path("upload/", views.upload_photos, name="upload_photos"),
    path("analyze/<int:doc_id>/", views.analyze_file, name="analyze_file"),
    path("get_text/<int:doc_id>/", views.get_text, name="get_text"),
    path(
        "confirm_payment/<int:doc_id>/", views.confirm_payment, name="confirm_payment"
    ),
    path("delete/<int:doc_id>/", views.delete_file, name="delete_file"),
    path("get_text/<int:doc_id>/", views.get_text, name="get_text"),
    path("cart/", views.view_cart, name="view_cart"),
    path("cart/add/<int:doc_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:doc_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/pay_all/", views.confirm_all_payments, name="confirm_all_payments"),
]
