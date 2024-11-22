from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render

from apps.users.forms import SimpleUserRegistrationForm


def login_view(request):
    error_message = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            print(f"Authenticated User: {user}")
            login(request, user)
            return redirect("main")
        else:
            error_message = "Неправильное имя пользователя или пароль."
            print("Authentication failed")
    return render(request, "auth/login.html", {"error_message": error_message})


def register(request):
    if request.method == "POST":
        form = SimpleUserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Вы успешно зарегистрировались! Теперь вы можете войти."
            )
            return redirect("login")
    else:
        form = SimpleUserRegistrationForm()
    return render(request, "auth/register.html", {"form": form})
