from django import forms   
from datetime import datetime
from main.models import Market,Pair


class MarketPairForm(forms.Form):
    market_list=[(item.market,item.market) for item in Market.objects.all()]
    market=forms.ChoiceField(choices=market_list,label="取引所",initial=market_list[0])
    
    init_market=Market.objects.all()[0]
    pair_list=[(item.pair,item.pair) for item in Pair.objects.filter(market=init_market)]
    pair=forms.ChoiceField(choices=pair_list,label="通貨ペア",initial=pair_list[0])
    
class TradeForm(forms.Form):
    action_choices=[("buy","buy"),("sell","sell")]
    action=forms.ChoiceField(choices=action_choices,initial=action_choices[0],label="買/売")

    lot=forms.FloatField(min_value=0.0,initial=0.0,label="数量")

    is_commit=forms.BooleanField(required=False,initial="False",widget=forms.HiddenInput())