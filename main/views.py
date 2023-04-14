from django.shortcuts import render
from .forms import Form
from django.views.generic import TemplateView
from .models import Pair,Market,OHLC
from .src import get_chart
from datetime import datetime,timedelta,date
from django.db.models import Max
from tqdm import tqdm
import pandas as pd

# Create your views here.

class IndexView(TemplateView):
    
    def get(self,request):
        params={
            "forms":Form(),
            "msg":"",
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

        ##取引所における通貨ペアを取得
        pair=Pair.objects.filter(market=market,pair=request_cp["pair"])[0] #今選択中の通貨ペア
        self.__create_ohlc(pair=pair) #更新があるときは新たなレコードを作成
        ##
        

        params={
            "forms":_form,
            "msg":f"{request_cp['market']},{request_cp['pair']},{request_cp['date']}",
        }

        return render(request=request,template_name="main/index.html",context=params)
    

    def __create_ohlc(self,pair:Pair):
        """
        通貨ペアのテーブルに更新があればレコードを追加する

        :param Pair pair:通貨ペアのモデルクラス
        """

        chart=pd.DataFrame([])

        latest:datetime=OHLC.objects.filter(pair=pair).aggregate(Max("date"))["date__max"] #最新データのdateを取得
        dday=(datetime.now().date()-latest).days #最新データと今の日数差
        if dday>0: #1日以上の差があるとき
            chart=get_chart(
                market=pair.market.market,pair=pair.pair,
                before=datetime.now(),
                after=datetime(year=latest.year,month=latest.month,day=latest.day)-timedelta(days=1), #少し前まで検索しておく
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
            
