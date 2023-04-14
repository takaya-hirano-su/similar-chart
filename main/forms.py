from django import forms   

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
        initial="2000-01-01",
        widget=forms.NumberInput(attrs={"type":"date"}) #入力をカレンダーに設定
    )

