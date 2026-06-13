from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login


def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto logowanie po rejestracji
            return redirect("wallet_dashboard")  # przekierowanie na panel główny
    else:
        form = UserCreationForm()
    return render(request, "wallet/register.html", {"form": form})


def wallet_dashboard_view(request):
    return render(request, "wallet/dashboard.html")
