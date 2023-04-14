from django.shortcuts import render
from .forms import Form
from django.views.generic import TemplateView
from .models import Pair,Market,OHLC
from .src import *
from datetime import datetime,timedelta,date
from django.db.models import Max
from tqdm import tqdm
import pandas as pd
from django_pandas.io import read_frame
import json

# Create your views here.

class IndexView(TemplateView):
    
    def get(self,request):
        params={
            "forms":Form(),
            "msg":"",
            "chart":{},
        }
        return render(request=request,template_name="main/index.html",context=params)
    
    def post(self,request):

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
        self.__create_ohlc(pair=pair) #更新があるときは新たなレコードを作成
        ##

        ##選択した通貨ペアをテーブルから読みだす
        ohlc=read_frame(
            self.__read_ohlc(pair=pair,date=request_cp["date"]),
            fieldnames=["pair","is_train_data","open","high","low","close","date"]
            )        
        ohlc["date"]=ohlc["date"].astype(str) #時間を文字列に変換.datetimeのままjsonにするとunixになってしまう.
        ##
        
        params={
            "forms":_form,
            "msg":f"{request_cp['market']},{request_cp['pair']},{request_cp['date']}",
            "chart":ohlc.to_json(),
        }

        return render(request=request,template_name="main/index.html",context=params)


    def __read_ohlc(self,pair:Pair,date:str):
        """
        dateからDAYS日前までのチャートを取得(DAYSはデフォルトで72日)

        :param Pair pair: 通貨ペアのモデルクラス
        :param str date: フォームで入力された日付
        """

        ##date-DAYS(72日)~dateの範囲における通貨ペアを取得
        date=datetime.strptime(date,"%Y-%m-%d")
        before=datetime(year=date.year,month=date.month,day=date.day,hour=9)
        after=before-timedelta(days=DAYS)
        ohlc=OHLC.objects\
            .filter(pair=pair)\
            .filter(date__gte=after.date())\
            .filter(date__lte=before.date())\
            .order_by("date")
        ##

        return ohlc

    def __create_ohlc(self,pair:Pair):
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
            
