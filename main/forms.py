from django import forms   
from django.db.models import Max

from datetime import datetime

from .src import DAYS
from .models import Market,Pair,OHLC

NOW=datetime.now().date() #現在の日にち

class Form (forms.Form):

    def __init__(self,*args,**kwargs):
        super(Form,self).__init__(*args,**kwargs)
        self.fields["market"].widget.attrs["class"]="form-select"
        self.fields["pair"].widget.attrs["class"]="form-select"
        self.fields["date"].widget.attrs["class"]="form-control"
        self.fields["past_days"].widget.attrs["class"]="form-control"
        self.fields["future_days"].widget.attrs["class"]="form-control"
        self.fields["similar_chart_num"].widget.attrs["class"]="form-control"

        
    market_list=[(item.market,item.market) for item in Market.objects.all()]
    market=forms.ChoiceField(choices=market_list,label="取引所",initial=market_list[0])
    
    init_market=Market.objects.all()[0]
    pair_list=[(item.pair,item.pair) for item in Pair.objects.filter(market=init_market)]
    pair=forms.ChoiceField(choices=pair_list,label="通貨ペア",initial=pair_list[0])
    

    date_latest=OHLC.objects.filter(
        pair=Pair.objects.filter(market=init_market)[0]
        ).aggregate(Max("date"))["date__max"] #データベースに登録済みのローソク足の最新日付
    
    date=forms.DateField(
        initial=date_latest,
        widget=forms.NumberInput(attrs={"type":"date","min":datetime(2020,1,1).date(),"max":date_latest}), #入力をカレンダーに設定
        label="日付"
    )
    
    init_days=DAYS
    past_days=forms.IntegerField(max_value=DAYS,min_value=5,initial=init_days,label="参照日数")

    init_future_days=15
    future_days=forms.IntegerField(max_value=30,min_value=1,initial=init_future_days,label="予測日数")

    init_chart_num=10
    similar_chart_num=forms.IntegerField(max_value=10,min_value=1,initial=init_chart_num,label="類似チャート数")
    similar_rank=forms.IntegerField(min_value=1,initial=1,widget=forms.HiddenInput())
