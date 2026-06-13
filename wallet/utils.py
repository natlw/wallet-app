from django.utils import timezone
from datetime import timedelta
from .models import AssetCache
from .services import get_crypto_price_from_api, get_fiat_price_from_api


def get_or_update_asset_price(asset):
    now = timezone.now()
    try:
        cache = AssetCache.objects.get(asset=asset)
        if now - cache.last_updated < timedelta(
            minutes=10
        ):  # czy catche starsze niż 10 minut
            return cache.price_pln
    except AssetCache.DoesNotExist:
        cache = None

    # nie istnieje lub stare catche, pobiera nowe dane z api
    new_price = None
    if asset.asset_type == "CRYPTO" and asset.api_id:
        new_price = get_crypto_price_from_api(asset.api_id)
    elif asset.asset_type == "FIAT":
        new_price = get_fiat_price_from_api(asset.symbol)

    # jak pobrało dane z api, to aktualizuje catche, nie to zwraca stare
    if new_price is not None:
        if cache:
            cache.price_pln = new_price
            cache.save()
        else:
            cache = AssetCache.objects.create(asset=asset, price_pln=new_price)
        return cache.price_pln

    if cache:
        return cache.price_pln

    return None
