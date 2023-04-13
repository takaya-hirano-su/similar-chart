import pandas as pd
from datetime import datetime,timedelta
import requests
from math import ceil
import time


def get_chart(market:str,pair:str,before:datetime,after:datetime,periods=60*60*12)->pd.DataFrame:
    """
    指定した取引所における通貨ペアの過去チャートを取ってくる関数

    :params str market: 取引所 [bitflyer, binance]
    :params str pair: 通貨ペア [btcjpy, ethjpy, btcusdt, ethusdt]
    :params datetime.datetime before:
    :params datetime.datetime after: after~beforeの期間でデータを取得する
    :params int periods: 取得する足の時間間隔. 単位はsec
    :return pandas.DataFrame chart: 過去チャート. [datetime,open,high,low,close]
    """

    base_url=f"https://api.cryptowat.ch/markets/{market}/{pair}/ohlc"
    col_name=["datetime","open","high","low","close","volume","quote_volume"]
    chart=pd.DataFrame(columns=col_name)
    
    data_num=1500 #1回のrequestで取るデータ数
    data_all=(before.timestamp()-after.timestamp())/periods #取得する全データ数
    request_num=ceil(data_all/data_num) #requestする回数
    for n in range(request_num):

        before_n=before-timedelta(seconds=periods*data_num*n)
        after_n=before_n-timedelta(seconds=periods*data_num) if data_all>data_num else after
        print("get from ",after_n,"~",before_n)
        url=base_url+f"?periods={periods}&after={int(after_n.timestamp())}&before={int(before_n.timestamp())}"
        response=requests.get(url).json() #urlにrequest
        
        if len(response["result"][f"{periods}"])==0: #指定した期間にデータが無ければbreak
            break

        if n==0:
            chart=pd.DataFrame(data=response["result"][f"{periods}"],columns=col_name) #pandasに格納
        else:
            chart_tmp=pd.DataFrame(data=response["result"][f"{periods}"],columns=col_name)
            chart=pd.concat([chart_tmp,chart],axis=0,ignore_index=True) #既に取得したデータに結合

    chart["datetime"]=chart["datetime"].apply(datetime.fromtimestamp) #timestampから日時に変換(日本時間)
    chart=chart.drop(labels=["volume","quote_volume"],axis=1)
    return chart


if __name__=="__main__":
    before=datetime.now()
    delta=timedelta(days=365*10)
    after=before-delta
    chart=get_chart(
        market="bitflyer",pair="btcjpy",
        before=before,after=after,periods=60*60*12
        )
    
    # chart.to_csv("chart.csv")