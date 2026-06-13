from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path(
        "admin/",
        admin.site.class_urls if hasattr(admin.site, "class_urls") else admin.site.urls,
    ),
    path("auth/", include("wallet.urls")),
    path(
        "", lambda request: redirect("login", permanent=False)
    ),  # przekierowanie do logowania
]
