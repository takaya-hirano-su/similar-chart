from django import forms   
from datetime import datetime

from main.models import Market,Pair
from .models import UserNetAsset,UserCurrnecy,UserCoin
from accounts.models import CustomUser


class MarketPairForm(forms.Form):

    def __init__(self,*args,**kwargs):
        super(MarketPairForm,self).__init__(*args,**kwargs)
        self.fields["market"].widget.attrs["class"]="form-select"
        self.fields["pair"].widget.attrs["class"]="form-select"

    market_list=[(item.market,item.market) for item in Market.objects.all()]
    market=forms.ChoiceField(choices=market_list,label="取引所",initial=market_list[0])
    
    init_market=Market.objects.all()[0]
    pair_list=[(item.pair,item.pair) for item in Pair.objects.filter(market=init_market)]
    pair=forms.ChoiceField(choices=pair_list,label="通貨ペア",initial=pair_list[0])
    
class TradeForm(forms.Form):

    def __init__(self,*args,**kwargs):
        super(TradeForm,self).__init__(*args,**kwargs)
        self.fields["action"].widget.attrs["class"]="form-select"
        self.fields["lot"].widget.attrs["class"]="form-control"
        
    action_choices=[("buy","buy"),("sell","sell")]
    action=forms.ChoiceField(choices=action_choices,initial=action_choices[0],label="買/売")

    lot=forms.FloatField(min_value=0.0001,initial=0,label="数量")

    is_commit=forms.BooleanField(required=False,initial="False",widget=forms.HiddenInput())


def custom_valid(action:str,lot:float,**kwargs)->str:
    """
    仮想通貨を売買するときに,自分の持ち金以上の数量を入力したらエラーにする関数
    
    :param str action: 'buy'か'sell'
    :param float lot: 売買数量
    
    where action=='buy'
    :param kwargs: {user_currency(ユーザーの持ち金),ask(買値)}
    :type kwargs: {UserCurrency,float}
    
    where action=='sell'
    :param kwargs: {user_coin(ユーザーの持ちコイン)}
    :type kwargs: {UserCoin}
    
    return error_msg: メッセージ. 問題ないときは空
    """
    
    error_msg=""
    
    if action=="buy":
        price_need=lot*kwargs["ask"] #購入に必要なお金
        error_msg="お金が足りません。入金してください。" if price_need>kwargs["user_currency"].price else error_msg
    
    elif action=="sell":
        error_msg="コインが足りません。" if lot>kwargs["user_coin"].lot else error_msg
    
    return error_msg
