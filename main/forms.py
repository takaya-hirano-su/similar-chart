from django import forms   

class Form (forms.Form):

    market=forms.ChoiceField(choices=[
        ("bitflyer","bitflyer"),("binance","binance"),
    ],label="market")
    pair=forms.ChoiceField(choices=[
        ("btcjpy","btcjpy"),("ethjpy","ethjpy"),
        ("btcusdt","btcusdt"),("ethusdt","ethusdt"),
    ],label="pair")
    date=forms.DateField(
        initial="2000-01-01",
        widget=forms.NumberInput(attrs={"type":"date"}) #入力をカレンダーに設定
    )
