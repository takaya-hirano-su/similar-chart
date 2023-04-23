from django import forms
from trade_training.models import Currency
from main.models import Market,Pair

class MarketCurrencyForm(forms.Form):

    market_init=Market.objects.all().first() #1つ目を初期化用の取引所とする
    market_choices=[(item.market,item.market) for item in Market.objects.all()]
    market=forms.ChoiceField(choices=market_choices,initial=market_choices[0],label="取引所")

    currency_choices=[]
    for currency in Currency.objects.all():
        for pair in Pair.objects.filter(market=market_init):
            if currency.currency.casefold() in pair.pair.casefold():
                currency_choices.append((currency.currency,currency.currency))
                break
    currency=forms.ChoiceField(choices=currency_choices,initial=currency_choices[0],label="通貨")


class DepositWithdrawForm(forms.Form):
    action=forms.ChoiceField(
        choices=[("deposit","入金"),("withdraw","出金")],
        initial=("deposit","入金"),
        label="入金 / 出金"
    )
    price=forms.FloatField(min_value=0.0,initial=0.0,label="金額")
    is_commit=forms.BooleanField(initial="False",widget=forms.HiddenInput(),required=False)