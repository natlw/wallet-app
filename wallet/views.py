from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import WalletTransaction, Asset, UserProfile, AssetCache
from .utils import get_or_update_asset_price
from decimal import Decimal, InvalidOperation
from django.contrib import messages


def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user, cash_balance_pln=Decimal("0.00"))
            login(request, user)
            return redirect("wallet_dashboard")
    else:
        form = UserCreationForm()
    return render(request, "wallet/register.html", {"form": form})


@login_required
def wallet_dashboard_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        if "refresh_prices" in request.POST:
            AssetCache.objects.all().delete()
            return redirect("wallet_dashboard")

        elif "add_funds" in request.POST:
            funds = request.POST.get("funds_amount")
            if funds:
                try:
                    profile.cash_balance_pln += Decimal(funds)
                    profile.save()
                except (InvalidOperation, ValueError):
                    pass
                return redirect("wallet_dashboard")

    transactions = WalletTransaction.objects.filter(user=request.user).select_related(
        "asset"
    )
    for tx in transactions:
        current_price = get_or_update_asset_price(tx.asset) or Decimal("0.0")
        current_value = tx.calculated_quantity * current_price
        tx.current_value_pln = current_value
        tx.profit_loss = current_value - tx.amount_in_pln

    portfolio_dict = {}
    total_invested_pln = Decimal("0.00")

    for tx in transactions:
        asset = tx.asset
        if asset not in portfolio_dict:
            portfolio_dict[asset] = {
                "quantity": Decimal("0.0"),
                "invested_cash": Decimal("0.0"),
            }

        portfolio_dict[asset]["quantity"] += tx.calculated_quantity
        portfolio_dict[asset]["invested_cash"] += tx.amount_in_pln
        total_invested_pln += tx.amount_in_pln

    portfolio_summary = []
    current_total_investments_value = Decimal("0.00")

    for asset, data in portfolio_dict.items():
        if data["quantity"] > 0:
            current_price = get_or_update_asset_price(asset) or Decimal("0.0")
            current_value = data["quantity"] * current_price
            current_total_investments_value += current_value

            portfolio_summary.append(
                {
                    "asset": asset,
                    "quantity": data["quantity"],
                    "invested_cash": data["invested_cash"],
                    "current_value_pln": current_value,
                    "is_cash": False,
                }
            )

    if profile.cash_balance_pln > 0:
        portfolio_summary.append(
            {
                "asset": type(
                    "AssetMock",
                    (object,),
                    {"name": "Niezainwestowane środki", "symbol": "PLN"},
                ),
                "quantity": profile.cash_balance_pln,
                "invested_cash": profile.cash_balance_pln,
                "current_value_pln": profile.cash_balance_pln,
                "is_cash": True,
            }
        )

    total_wealth_value = current_total_investments_value + profile.cash_balance_pln

    colors = ["#12A4D0", "#004067", "#FCA637", "#DE91CF", "#F0238A"]
    chart_labels = []
    chart_data = []
    chart_colors = []

    for i, item in enumerate(portfolio_summary):
        if total_wealth_value > 0:
            percentage = (item["current_value_pln"] / total_wealth_value) * 100
        else:
            percentage = 0
        item["percentage"] = round(percentage, 2)
        item["color"] = colors[i % len(colors)]

        chart_labels.append(item["asset"].name)
        chart_data.append(float(item["current_value_pln"]))
        chart_colors.append(item["color"])

    profit_loss = current_total_investments_value - total_invested_pln

    context = {
        "profile": profile,
        "portfolio_summary": portfolio_summary,
        "current_total_investments_value": current_total_investments_value,
        "profit_loss": profit_loss,
        "transactions": transactions,
        "chart_labels": chart_labels,
        "chart_data": chart_data,
        "chart_colors": chart_colors,
    }
    return render(request, "wallet/dashboard.html", context)


@login_required
def invest_view(request):
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == "POST":
        asset_symbol = request.POST.get("asset_symbol")
        amount_pln_str = request.POST.get("amount_pln")

        if not asset_symbol or not amount_pln_str:
            return redirect("invest_page")

        try:
            amount_pln = Decimal(amount_pln_str)
        except InvalidOperation:
            messages.error(request, "Nieprawidłowa kwota.")
            return redirect("invest_page")

        if profile.cash_balance_pln < amount_pln:
            messages.error(request, "Nie masz wystarczających środków na koncie.")
            return redirect("invest_page")

        asset = get_object_or_404(Asset, symbol=asset_symbol)
        current_price = get_or_update_asset_price(asset)

        if not current_price or current_price == 0:
            return redirect("invest_page")

        calculated_qty = amount_pln / current_price

        WalletTransaction.objects.create(
            user=request.user,
            asset=asset,
            amount_in_pln=amount_pln,
            calculated_quantity=calculated_qty,
            price_per_unit=current_price,
        )

        profile.cash_balance_pln -= amount_pln
        profile.save()

        return redirect("wallet_dashboard")

    return render(request, "wallet/invest.html")


@login_required
def delete_transaction_view(request, pk):
    transaction = get_object_or_404(WalletTransaction, id=pk, user=request.user)
    profile = get_object_or_404(UserProfile, user=request.user)

    current_price = get_or_update_asset_price(transaction.asset)

    if current_price:
        sell_value = transaction.calculated_quantity * current_price
    else:
        sell_value = transaction.amount_in_pln

    profile.cash_balance_pln += sell_value
    profile.save()

    transaction.delete()
    return redirect("wallet_dashboard")
