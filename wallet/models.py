from django.db import models
from django.contrib.auth.models import User


class Asset(models.Model):
    ASSET_TYPES = [
        ("CRYPTO", "Kryptowaluta"),
        ("FIAT", "Waluta tradycyjna (FIAT)"),
    ]

    name = models.CharField(
        max_length=100, verbose_name="Pełna nazwa (np. Bitcoin, Dolar)"
    )
    symbol = models.CharField(
        max_length=10, unique=True, verbose_name="Skrót / Symbol (np. BTC, USD)"
    )
    asset_type = models.CharField(
        max_length=10,
        choices=ASSET_TYPES,
        default="CRYPTO",
        verbose_name="Rodzaj waluty",
    )
    api_id = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="ID w API (np. bitcoin)"
    )

    def __str__(self):
        return f"{self.name} ({self.symbol})"


class WalletTransaction(models.Model):
    TRANSACTION_TYPES = [
        ("BUY", "Kupno"),
        ("SELL", "Sprzedaż"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="transactions",
        verbose_name="Użytkownik",
    )
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name="transactions",
        verbose_name="Wybrana waluta",
    )
    transaction_type = models.CharField(
        max_length=4, choices=TRANSACTION_TYPES, verbose_name="Typ operacji"
    )
    quantity = models.DecimalField(
        max_digits=18, decimal_places=8, verbose_name="Ilość (ile sztuk)"
    )
    price_per_unit = models.DecimalField(
        max_digits=14, decimal_places=4, verbose_name="Cena za 1 sztukę (w PLN)"
    )
    date = models.DateTimeField(verbose_name="Data i czas")

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} {self.quantity} {self.asset.symbol}"


class AssetCache(models.Model):
    asset = models.OneToOneField(
        Asset, on_delete=models.CASCADE, primary_key=True, verbose_name="Waluta"
    )
    price_pln = models.DecimalField(
        max_digits=14, decimal_places=4, verbose_name="Aktualny kurs w PLN"
    )
    last_updated = models.DateTimeField(
        auto_now=True, verbose_name="Ostatnia aktualizacja kursu"
    )

    def __str__(self):
        return f"Kurs {self.asset.symbol}: {self.price_pln} PLN (Aktualizacja: {self.last_updated})"
