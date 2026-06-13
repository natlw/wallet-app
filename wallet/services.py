import requests
from decimal import Decimal


def get_crypto_price_from_api(api_id):
    url = (
        f"https://api.coingecko.com/api/v3/simple/price?ids={api_id}&vs_currencies=pln"
    )
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if api_id in data and "pln" in data[api_id]:
                return Decimal(str(data[api_id]["pln"]))
    except Exception:
        pass
    return None


def get_fiat_price_from_api(symbol):
    if symbol.upper() == "PLN":
        return Decimal("1.0000")
    url = f"https://api.nbp.pl/api/exchangerates/rates/a/{symbol}/?format=json"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "rates" in data and len(data["rates"]) > 0:
                return Decimal(str(data["rates"][0]["mid"]))
    except Exception:
        pass
    return None
