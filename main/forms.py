from django import forms   
from datetime import datetime

NOW=datetime.now().date() #現在の日にち

class Form (forms.Form):

    market_list=[("bitflyer","bitflyer"),("binance","binance"),]
    market=forms.ChoiceField(
        choices=market_list,label="market",initial=market_list[0])
    pair_list=[
        ("btcjpy","btcjpy"),("ethjpy","ethjpy"),
        # ("btcusdt","btcusdt"),("ethusdt","ethusdt"),
        ]
    pair=forms.ChoiceField(choices=pair_list,label="pair",initial=pair_list[0])
    date=forms.DateField(
        initial=str(NOW),
        widget=forms.NumberInput(attrs={"type":"date"}) #入力をカレンダーに設定
    )
    similar_chart_num=forms.IntegerField(max_value=10,min_value=1,initial=5)

