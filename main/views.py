from pathlib import Path
PARENT=str(Path(__file__).parent)

from django.shortcuts import render
from .forms import Form
from django.views.generic import TemplateView
from .models import Pair,Market,OHLC
from .src.crypto_watch_API import get_chart
from .src.params import *
from datetime import datetime,timedelta,date
from django.db.models import Max,Min
import pandas as pd
from django_pandas.io import read_frame
import json
import numpy as np
from .apps import crypto_auto_encoder


class IndexView(TemplateView):
    
    def get(self,request):

        init_pair=Pair.objects.all()[0]

        ##選択した通貨ペアをテーブルから読みだす
        ohlc=read_frame(
            read_ohlc(pair=init_pair,date=str(Form.date_latest),past_days=Form.init_days),
            fieldnames=["pair","is_train_data","open","high","low","close","date"]
            )        
        
        ohlc_train=OHLC.objects.filter(pair=init_pair).filter(is_train_data=True).order_by("date")
        ohlc_train=read_frame(
            ohlc_train,
            fieldnames=["pair","is_train_data","open","high","low","close","date"]
        )
        ##

        ##似たチャートをAIによって選ぶ
        similar_charts,similar_charts_scaled=crypto_auto_encoder.get_similar_chart(
            chart=ohlc,chart_past=ohlc_train,similar_chart_num=Form().init_chart_num,
            past_days=Form().init_days,future_days=Form().init_future_days,
        )
        ##

        ##選びだしたチャートをjavascriptに渡すためにjsonに変換
        similar_chart_json={}
        for i in range(len(similar_charts)):
            similar_charts[i].loc[:,"date"]=similar_charts[i]["date"].values.astype(str)
            similar_charts_scaled[i].loc[:,"date"]=similar_charts_scaled[i]["date"].values.astype(str)
            similar_chart_json[f"No{i+1}"]={
                "original":similar_charts[i].to_dict(),
                "scaled":similar_charts_scaled[i].to_dict(),
                }
        similar_chart_json=json.dumps(similar_chart_json,ensure_ascii=False)

        ohlc["date"]=ohlc["date"].astype(str) #時間を文字列に変換.datetimeのままjsonにするとunixになってしまう.
        ##
        
        similar_canvas_ids=[f"canvas-No{i+1}" for i in np.arange(len(similar_charts),dtype=int)]
        similar_button_ids=[f"button-No{i+1}" for i in range(len(similar_canvas_ids))]

        params={
            "forms":Form(),
            "chart":ohlc.to_json(),
            "similar_chart":similar_chart_json,
            "similar_canvas_ids":similar_canvas_ids,
            "similar_button_ids":similar_button_ids,
        }
        return render(request=request,template_name="main/index.html",context=params)
    

    def post(self,request):

        print(request.POST)

        market=Market.objects.filter(market=request.POST["market"])[0]
        choices=Pair.objects.filter(market=market)
        choices=[choice.pair for choice in choices]

        ##取引所で扱ってない通貨ペアが入力されたら強制的に書き換える
        request_cp=request.POST.copy() #そのままでは書き換えられないからコピー
        if not request.POST["pair"] in choices: #書き換え
            request_cp["pair"]=choices[0]
        ##

        ##通貨ペアを取引所で扱ってるものだけにする
        _form=Form(request_cp)
        _form.fields["pair"].choices=[(choice,choice) for choice in choices] 
        _form.base_fields["pair"].choices=[(choice,choice) for choice in choices] 
        ##

        ##取引所における通貨ペアの取得＆更新
        pair=Pair.objects.filter(market=market,pair=request_cp["pair"])[0] #今選択中の通貨ペア
        ##

        ##選択した通貨ペアをテーブルから読みだす
        ohlc=read_frame(
            read_ohlc(pair=pair,date=request_cp["date"],past_days=int(request_cp["past_days"])),
            fieldnames=["pair","is_train_data","open","high","low","close","date"]
            )        
        
        
        ohlc_train=OHLC.objects.filter(pair=pair).filter(is_train_data=True).order_by("date")
        ohlc_train=read_frame(
            ohlc_train,
            fieldnames=["pair","is_train_data","open","high","low","close","date"]
        )
        ##

        ##似たチャートをAIによって選ぶ
        similar_charts,similar_charts_scaled=crypto_auto_encoder.get_similar_chart(
            chart=ohlc,chart_past=ohlc_train,similar_chart_num=int(request.POST["similar_chart_num"]),
            past_days=int(request_cp["past_days"]),future_days=int(request_cp["future_days"]),
        )
        ##

        ##選びだしたチャートをjavascriptに渡すためにjsonに変換
        similar_chart_json={}
        for i in range(len(similar_charts)):
            similar_charts[i].loc[:,"date"]=similar_charts[i]["date"].values.astype(str)
            similar_charts_scaled[i].loc[:,"date"]=similar_charts_scaled[i]["date"].values.astype(str)
            similar_chart_json[f"No{i+1}"]={
                "original":similar_charts[i].to_dict(),
                "scaled":similar_charts_scaled[i].to_dict(),
                }
        similar_chart_json=json.dumps(similar_chart_json,ensure_ascii=False)

        ohlc["date"]=ohlc["date"].astype(str) #時間を文字列に変換.datetimeのままjsonにするとunixになってしまう.
        ##
        
        similar_canvas_ids=[f"canvas-No{i+1}" for i in np.arange(len(similar_charts),dtype=int)]
        similar_button_ids=[f"button-No{i+1}" for i in range(len(similar_canvas_ids))]

        params={
            "forms":_form,
            "chart":ohlc.to_json(),
            "similar_chart":similar_chart_json,
            "similar_canvas_ids":similar_canvas_ids,
            "similar_button_ids":similar_button_ids,
        }

        return render(request=request,template_name="main/index.html",context=params)


def read_ohlc(pair:Pair,date:str,past_days:int):
    """
    dateからpast_days日前までのチャートを取得
    :param Pair pair: 通貨ペアのモデルクラス
    :param str date: フォームで入力された日付
    :param int past_days: フォームで入力された日数
    """
    ##date-DAYS(72日)~dateの範囲における通貨ペアを取得
    date=datetime.strptime(date,"%Y-%m-%d")
    before=datetime(year=date.year,month=date.month,day=date.day,hour=9)
    after=before-timedelta(days=past_days-1)
    ohlc=OHLC.objects\
        .filter(pair=pair)\
        .filter(date__gte=after.date())\
        .filter(date__lte=before.date())\
        .order_by("date")
    ##
    return ohlc


def create_ohlc(pair:Pair):
    """
    通貨ペアのテーブルに更新があればレコードを追加する
    :param Pair pair:通貨ペアのモデルクラス
    """
    chart=pd.DataFrame([])
    latest:datetime=OHLC.objects.filter(pair=pair).aggregate(Max("date"))["date__max"] #最新データのdateを取得
    dday=(datetime.now().date()-latest).days #最新データと今の日数差
    if dday>0: #1日以上の差があるとき新しいデータを取得する
        chart=get_chart(
            market=pair.market.market,pair=pair.pair,
            before=datetime.now(),
            after=datetime(year=latest.year,month=latest.month,day=latest.day)-timedelta(days=1), #少し前まで検索しておく
            periods=PERIODS
        )
        print(f"***new data***\n{chart}\n******")
    ##取得したデータの保存
    for _,c in (chart.iterrows()):
        open=c["open"]
        high=c["high"]
        low=c["low"]
        close=c["close"]
        date=str(c["datetime"].date())
        is_train_data=False
        ###取得したデータのレコードが無ければ追加する
        record=OHLC.objects.filter(pair=pair).filter(date=date)
        if len(record)==0:
            ohlc=OHLC(
                pair=pair,is_train_data=is_train_data,
                open=open,high=high,low=low,close=close,
                date=date
            )
            ohlc.save()
        ##
    ##
            
