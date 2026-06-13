from django.contrib import admin
from .models import Asset, WalletTransaction, AssetCache, UserProfile


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ("name", "symbol", "asset_type", "api_id")
    search_fields = ("name", "symbol")


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "asset",
        "amount_in_pln",
        "calculated_quantity",
        "price_per_unit",
        "date",
    )
    list_filter = ("asset", "date")


@admin.register(AssetCache)
class AssetCacheAdmin(admin.ModelAdmin):
    list_display = ("asset", "price_pln", "last_updated")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "cash_balance_pln")
