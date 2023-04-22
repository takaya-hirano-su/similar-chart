from django import forms   
from datetime import datetime
from main.models import Market,Pair


class MarketPairForm(forms.Form):
    market_list=[(item.market,item.market) for item in Market.objects.all()]
    market=forms.ChoiceField(choices=market_list,label="market",initial=market_list[0])
    
    init_market=Market.objects.all()[0]
    pair_list=[(item.pair,item.pair) for item in Pair.objects.filter(market=init_market)]
    pair=forms.ChoiceField(choices=pair_list,label="pair",initial=pair_list[0])
    
class TradeForm(forms.Form):
    action_choices=[("buy","buy"),("sell","sell")]
    action=forms.ChoiceField(choices=action_choices,initial=action_choices[0])

    lot=forms.FloatField(min_value=0.00001)