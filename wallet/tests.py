from decimal import Decimal
from unittest.mock import patch
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from wallet.models import Asset, WalletTransaction, AssetCache, UserProfile
from wallet.services import get_crypto_price_from_api, get_fiat_price_from_api
from wallet.utils import get_or_update_asset_price


# 1. MODELE (models.py)
class AssetModelTest(TestCase):
    # test metody str, czy zwraca dobrą nazwe i symbol
    def test_str_representation(self):
        asset = Asset(name="Bitcoin", symbol="BTC", asset_type="CRYPTO")
        self.assertEqual(str(asset), "Bitcoin (BTC)")


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass1234!")

    # test czy nowy profil ma domyślnie 0PLN
    def test_default_cash_balance_is_zero(self):
        profile = UserProfile.objects.create(user=self.user)
        self.assertEqual(profile.cash_balance_pln, Decimal("0.00"))


# 2. SERWISY - API (services.py)
class FiatServiceTest(TestCase):
    # sprawdza czy przy pobraniu PLN daje 1PLN
    # próba: wywołanie funkcji z symbolem "PLN" bez żadnego połączenia
    def test_pln_returns_one_without_hitting_api(self):
        result = get_fiat_price_from_api("PLN")
        self.assertEqual(result, Decimal("1.0000"))

    @patch("wallet.services.requests.get")
    # gdy zewnętrzne api wywoła wyjatek, zwracane jest none nie ma crash
    # próba: wywołanie funkcji gdy połączenie z API pada i rzuca wyjątek timeout
    def test_returns_none_when_api_raises_exception(self, mock_get):
        mock_get.side_effect = Exception("timeout")
        result = get_fiat_price_from_api("EUR")
        self.assertIsNone(result)


class CryptoServiceTest(TestCase):
    @patch("wallet.services.requests.get")
    # sprawdza czy funkcja poprawnie odczytuje cenę bitcoina z odpowiedzi coingecko i zwraca ją jako Decimal
    # próba: wywołanie funkcji gdy API odpowiada poprawnym jsonem z ceną bitcoina
    def test_returns_price_from_coingecko_response(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"bitcoin": {"pln": 250000.0}}
        result = get_crypto_price_from_api("bitcoin")
        self.assertEqual(result, Decimal("250000.0"))


# 3. logika cache (utils.py)
class GetOrUpdateAssetPriceTest(TestCase):
    def setUp(self):
        self.asset = Asset.objects.create(
            name="Bitcoin", symbol="BTC", asset_type="CRYPTO", api_id="bitcoin"
        )

    @patch("wallet.utils.get_crypto_price_from_api")
    # sprawdza czy gdy cache ma mniej niż 10 minut, zwracana jest zapisana cena bez odpytywania API
    # próba: wywołanie funkcji gdy w bazie istnieje świeży rekord cache z ceną bitcoina
    def test_fresh_cache_skips_api(self, mock_api):
        AssetCache.objects.create(asset=self.asset, price_pln=Decimal("150000.00"))
        price = get_or_update_asset_price(self.asset)
        self.assertEqual(price, Decimal("150000.00"))
        mock_api.assert_not_called()

    @patch("wallet.utils.get_crypto_price_from_api")
    # sprawdza czy gdy cache ma więcej niż 10 minut, pobierana jest nowa cena z API i zapisywana do bazy
    # próba: wywołanie funkcji gdy rekord cache ma sztucznie przestawiony czas na 15 minut wstecz
    def test_expired_cache_updates_from_api(self, mock_api):
        cache = AssetCache.objects.create(
            asset=self.asset, price_pln=Decimal("10000.00")
        )
        AssetCache.objects.filter(pk=cache.pk).update(
            last_updated=timezone.now() - timedelta(minutes=15)
        )
        mock_api.return_value = Decimal("13500.00")

        price = get_or_update_asset_price(self.asset)
        self.assertEqual(price, Decimal("13500.00"))

        cache.refresh_from_db()
        self.assertEqual(cache.price_pln, Decimal("13500.00"))

    @patch("wallet.utils.get_crypto_price_from_api")
    # sprawdza czy gdy cache wygasł ale API zwraca błąd (None), zwracana jest stara cena z cache zamiast crasha
    # próba: wywołanie funkcji gdy cache wygasł i API nie może zwrócić nowej ceny
    def test_fallback_to_stale_cache_when_api_fails(self, mock_api):
        cache = AssetCache.objects.create(
            asset=self.asset, price_pln=Decimal("10000.00")
        )
        AssetCache.objects.filter(pk=cache.pk).update(
            last_updated=timezone.now() - timedelta(minutes=15)
        )
        mock_api.return_value = None

        price = get_or_update_asset_price(self.asset)
        self.assertEqual(price, Decimal("10000.00"))


# 4. TEST INTEGRACYJNY (views.py)
class InvestIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="investor", password="password123"
        )
        self.profile = UserProfile.objects.create(
            user=self.user, cash_balance_pln=Decimal("5000.00")
        )
        self.asset = Asset.objects.create(
            name="Bitcoin", symbol="BTC", asset_type="CRYPTO", api_id="bitcoin"
        )
        AssetCache.objects.create(asset=self.asset, price_pln=Decimal("200000.00"))
        self.client.login(username="investor", password="password123")

    # sprawdza czy gdy użytkownik nie ma wystarczających środków, saldo się nie zmienia i transakcja nie powstaje
    # próba: POST na invest_page z kwotą 6000 PLN przy saldzie 5000 PLN
    def test_investment_blocked_when_funds_insufficient(self):
        self.client.post(
            reverse("invest_page"),
            {"asset_symbol": "BTC", "amount_pln": "6000.00"},
        )
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.cash_balance_pln, Decimal("5000.00"))
        self.assertEqual(WalletTransaction.objects.filter(user=self.user).count(), 0)
