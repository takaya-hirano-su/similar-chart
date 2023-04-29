from django import forms
from trade_training.models import Currency,UserCurrnecy
from main.models import Market,Pair

class MarketCurrencyForm(forms.Form):

    def __init__(self,*args,**kwargs):
        super(MarketCurrencyForm,self).__init__(*args,**kwargs)
        self.fields["market"].widget.attrs["class"]="form-select"
        self.fields["currency"].widget.attrs["class"]="form-select"

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

    def __init__(self,*args,**kwargs):
        super(DepositWithdrawForm,self).__init__(*args,**kwargs)
        self.fields["action"].widget.attrs["class"]="form-select"
        self.fields["price"].widget.attrs["class"]="form-control"

    action=forms.ChoiceField(
        choices=[("deposit","入金"),("withdraw","出金")],
        initial=("deposit","入金"),
        label="入金 / 出金"
    )
    price=forms.FloatField(min_value=0.0001,initial=0,label="金額")
    is_commit=forms.BooleanField(initial="False",widget=forms.HiddenInput(),required=False)

def custom_valid(price:float,user_currency:UserCurrnecy)->str:
    """
    お金を引き出すときに,持ち金以上を引き出そうとしていないかチェックする関数

    :param float price: 引き出そうとしている金額
    :param user_currency: 持ち金クラス
    :type user_currency: UserCurrency

    :return str error_msg: エラーメッセージ. エラーのないときは空
    """

    error_msg= "残高以上の金額は引き出せません。" if price>user_currency.price else ""

    return error_msg