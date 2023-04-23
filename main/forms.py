from django import forms   
from datetime import datetime
from .src import DAYS
from .models import Market,Pair

NOW=datetime.now().date() #現在の日にち

class Form (forms.Form):

    market_list=[(item.market,item.market) for item in Market.objects.all()]
    market=forms.ChoiceField(choices=market_list,label="market",initial=market_list[0])
    
    init_market=Market.objects.all()[0]
    pair_list=[(item.pair,item.pair) for item in Pair.objects.filter(market=init_market)]
    pair=forms.ChoiceField(choices=pair_list,label="pair",initial=pair_list[0])
    
    date=forms.DateField(
        initial=str(NOW),
        widget=forms.NumberInput(attrs={"type":"date","min":datetime(2020,1,1).date()}) #入力をカレンダーに設定
    )
    
    past_days=forms.IntegerField(max_value=DAYS,min_value=5,initial=DAYS)
    future_days=forms.IntegerField(max_value=30,min_value=1,initial=15)

    similar_chart_num=forms.IntegerField(max_value=10,min_value=1,initial=10,label="Chart Num")
    similar_rank=forms.IntegerField(min_value=1,initial=1,widget=forms.HiddenInput())
