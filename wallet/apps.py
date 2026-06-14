from django.apps import AppConfig


class WalletConfig(AppConfig):
    name = "wallet"

    def ready(self):
        from django.db import connection

        try:
            if "wallet_asset" in connection.introspection.table_names():
                from .models import Asset

                assets = [
                    {
                        "name": "Bitcoin",
                        "symbol": "BTC",
                        "asset_type": "CRYPTO",
                        "api_id": "bitcoin",
                    },
                    {
                        "name": "Ethereum",
                        "symbol": "ETH",
                        "asset_type": "CRYPTO",
                        "api_id": "ethereum",
                    },
                    {
                        "name": "Dolar amerykański",
                        "symbol": "USD",
                        "asset_type": "FIAT",
                        "api_id": None,
                    },
                    {
                        "name": "Frank szwajcarski",
                        "symbol": "CHF",
                        "asset_type": "FIAT",
                        "api_id": None,
                    },
                ]
                for a in assets:
                    Asset.objects.get_or_create(symbol=a["symbol"], defaults=a)
        except Exception:
            pass
