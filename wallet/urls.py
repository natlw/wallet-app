from django.urls import path, include
from .views import (
    register_view,
    wallet_dashboard_view,
    invest_view,
    delete_transaction_view,
)

urlpatterns = [
    path("", include("django.contrib.auth.urls")),
    path("register/", register_view, name="register"),
    path("dashboard/", wallet_dashboard_view, name="wallet_dashboard"),
    path("invest/", invest_view, name="invest_page"),
    path(
        "transaction/<int:pk>/delete/",
        delete_transaction_view,
        name="delete_transaction",
    ),
]
