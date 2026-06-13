from django.contrib import admin
from .models import Asset, WalletTransaction, AssetCache


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    # kolumny
    list_display = ("name", "symbol", "asset_type", "api_id")
    # filtry
    list_filter = ("asset_type",)
    # wyszukiwanie
    search_fields = ("name", "symbol")


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "asset",
        "transaction_type",
        "quantity",
        "price_per_unit",
        "date",
    )
    list_filter = ("transaction_type", "date", "asset")
    search_fields = ("user__username", "asset__name")


@admin.register(AssetCache)
class AssetCacheAdmin(admin.ModelAdmin):
    list_display = ("asset", "price_pln", "last_updated")
