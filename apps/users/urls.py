from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .views import LoginView

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("register/", views.RegisterView.as_view(), name="register"),
]
