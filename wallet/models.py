from django.db import models
from django.contrib.auth.models import User


class Asset(models.Model):
    ASSET_TYPES = (
        ("CRYPTO", "Kryptowaluta"),
        ("FIAT", "Waluta tradycyjna"),
    )
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=10, unique=True)
    asset_type = models.CharField(max_length=10, choices=ASSET_TYPES)
    api_id = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.symbol})"


class WalletTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    amount_in_pln = models.DecimalField(max_digits=20, decimal_places=2)
    calculated_quantity = models.DecimalField(
        max_digits=20, decimal_places=8, default=0.0
    )
    price_per_unit = models.DecimalField(max_digits=20, decimal_places=4)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.asset.symbol} za {self.amount_in_pln} PLN"


class AssetCache(models.Model):
    asset = models.OneToOneField(Asset, on_delete=models.CASCADE)
    price_pln = models.DecimalField(max_digits=20, decimal_places=4)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cache {self.asset.symbol}: {self.price_pln} PLN"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cash_balance_pln = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00
    )

    def __str__(self):
        return f"Profil: {self.user.username} (Gotówka: {self.cash_balance_pln} PLN)"
