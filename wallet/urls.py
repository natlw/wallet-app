from django.urls import path, include
from .views import register_view, wallet_dashboard_view

urlpatterns = [
    path("", include("django.contrib.auth.urls")),
    path("register/", register_view, name="register"),  # rejestracja
    path("dashboard/", wallet_dashboard_view, name="wallet_dashboard"),  # panel główny
]
