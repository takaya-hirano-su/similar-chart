from django.shortcuts import render
from django.views.generic import TemplateView
from django.shortcuts import redirect

from datetime import datetime
import json
import numpy as np
import pandas as pd
from copy import deepcopy

from deposit.forms import MarketCurrencyForm
from main.models import Market,Pair,OHLC
from accounts.models import CustomUser
from trade_training.models import UserNetAsset,Currency,UserCurrnecy,UserCoin,BidAsk
from trade_training.views import init_net_asset,create_net_asset,init_update_quote,get_currency_list

# Create your views here.

class HomeView(TemplateView):

    def get(self,request):

        if not request.user.is_authenticated: #ログインしていなければsignup画面にリダイレクト
            return redirect(to="/accounts/signup")
        
        now=datetime.now()

        initial_market=Market.objects.all()[0] #取引所の初期値
        initial_currency:Currency=get_currency_list(market=initial_market)[0] #通貨の初期値

        user_id=request.user.id 
        user=CustomUser.objects.get(id=user_id)
        is_user_asset=True if not len(UserNetAsset.objects.filter(user=user,market=initial_market))==0 else False
        if not is_user_asset: #総資産情報がないときは初期化
            init_net_asset(user=user,now=now)

        #現在の資産情報の有無
        is_current=True if not len(UserNetAsset.objects.filter(user=user,date=now.date(),market=initial_market))==0 else False
        if not is_current:
            create_net_asset(user=user,now=now,market=initial_market) #今日の情報がないときは新たに作成

        #現在のユーザーの資産情報の取得  
        user=CustomUser.objects.get(id=request.user.id)
        net_asset=UserNetAsset.objects.filter(user=user,market=initial_market).order_by("date").last() #最新の情報を取得
        user_currency=UserCurrnecy.objects.get(net_asset=net_asset,currency=initial_currency)
        user_coins={}
        for user_coin in UserCoin.objects.filter(net_asset=net_asset):
            if initial_currency.currency.casefold() in user_coin.pair.pair.casefold():

                #気配値情報の新規登録or更新
                init_update_quote(market=initial_market,pair=user_coin.pair,now=now) 
                quote=BidAsk.objects.get(pair=user_coin.pair) #更新後のデータを取得
                user_coins[user_coin.pair.pair]={
                    "bid":quote.bid,"lot":user_coin.lot
                }                
        user_coins=json.dumps(user_coins,ensure_ascii=False)

        #ユーザーの資産の遷移情報の取得
        chart_dates,user_chart=get_user_chart(
            user=user,market=initial_market,
            currency=initial_currency,now=now
        )

        params={
            "market_currency_form":MarketCurrencyForm(),
            "user_currency":user_currency,
            "user_coins":user_coins,
            "user_chart":user_chart,
            "chart_dates":chart_dates,
        }

        return render(request=request,template_name="home/home.html",context=params)
    

    def post(self,request):

        now=datetime.now() #現在時刻

        user=CustomUser.objects.get(id=request.user.id) #ユーザー情報
        
        market=Market.objects.get(market=request.POST["market"]) #formで選択したmarket
        currency_list=get_currency_list(market=market) #取引所が扱っている通貨リスト
        currency=Currency(currency=request.POST["currency"])

        #取り扱っていない通貨が選択されたら,扱っているものに変える
        request_post=request.POST.copy()
        if not currency.id in [item.id for item in currency_list]:
            request_post["currency"]=currency_list[0].currency
            currency=currency_list[0]
        market_currency_form=MarketCurrencyForm(request_post)
        market_currency_form.fields["currency"].choices=[(item.currency,item.currency) for item in currency_list]
        market_currency_form.base_fields["currency"].choices=[(item.currency,item.currency) for item in currency_list]

        #現在の資産情報の有無
        is_current=True if not len(UserNetAsset.objects.filter(user=user,date=now.date(),market=market))==0 else False
        if not is_current:
            create_net_asset(user=user,now=now,market=market) #今日の情報がないときは新たに作成

        #現在のユーザーの資産情報の取得  
        user=CustomUser.objects.get(id=request.user.id)
        net_asset=UserNetAsset.objects.filter(user=user,market=market).order_by("date").last() #最新の情報を取得
        user_currency=UserCurrnecy.objects.get(net_asset=net_asset,currency=currency)
        user_coins={}
        for user_coin in UserCoin.objects.filter(net_asset=net_asset):
            if currency.currency.casefold() in user_coin.pair.pair.casefold():

                #気配値情報の新規登録or更新
                init_update_quote(market=market,pair=user_coin.pair,now=now) 
                quote=BidAsk.objects.get(pair=user_coin.pair) #更新後のデータを取得
                user_coins[user_coin.pair.pair]={
                    "bid":quote.bid,"lot":user_coin.lot
                }                
        user_coins=json.dumps(user_coins,ensure_ascii=False)

        #ユーザーの資産の遷移情報の取得
        chart_dates,user_chart=get_user_chart(
            user=user,market=market,
            currency=currency,now=now
        )

        params={
            "market_currency_form":MarketCurrencyForm(request_post),
            "user_currency":user_currency,
            "user_coins":user_coins,
            "user_chart":user_chart,
            "chart_dates":chart_dates,
        }

        return render(request=request,template_name="home/home.html",context=params)

def get_user_chart(user:CustomUser,market:Market,currency:Currency,now:datetime):
    """
    ユーザーの資産遷移情報を計算し取得する関数
    """

    net_asset_chart=UserNetAsset.objects.filter(user=user,market=market).order_by("date")
    chart_dates=pd.DataFrame(
        data=UserNetAsset.objects.filter(user=user,market=market).order_by("date").values_list("date"),
    ).astype(str).to_json()
    pair_list=get_pair_list(market=market,currency=currency)

    ohlc_latest=OHLC.objects.all().order_by("date").last() #ローソク足の最新の日付
    if now.date()==ohlc_latest.date: #ローソク足データの最新の日付に現在時刻が入ってるとき
        user_currency_chart=np.array(UserCurrnecy.objects.filter(net_asset__in=net_asset_chart,currency=currency)\
            .order_by("net_asset__date").values_list("price"))
        for pair in pair_list:
            user_coins_chart=np.array(UserCoin.objects.filter(net_asset__in=net_asset_chart)\
                .filter(pair=pair).order_by("net_asset__date").values_list("lot"))
            ohlc=np.array(OHLC.objects.filter(pair=pair)\
                .filter(date__in=UserNetAsset.objects.filter(user=user,market=market).values_list("date"))\
                .order_by("date").values_list("close"))
            
            user_currency_chart+=user_coins_chart*ohlc
        user_chart=pd.Series(data=user_currency_chart.flatten(),name="user_chart").to_json()
        
    else: #まだ今日の日足が登録されていない時
        user_currency_chart=np.array(UserCurrnecy.objects.filter(net_asset__in=net_asset_chart,currency=currency)\
            .order_by("net_asset__date").values_list("price"))
        
        for pair in pair_list:
            #気配値情報の新規登録or更新
            init_update_quote(market=market,pair=pair,now=now) 
            quote=BidAsk.objects.get(pair=pair) #更新後のデータを取得
            bid=np.array(quote.bid).reshape(1,1) #これを今の価格とする

            user_coins_chart=np.array(UserCoin.objects.filter(net_asset__in=net_asset_chart)\
                .filter(pair=pair).order_by("net_asset__date").values_list("lot"))
            ohlc=np.array(OHLC.objects.filter(pair=pair)\
                .filter(date__in=UserNetAsset.objects.filter(user=user,market=market).values("date"))\
                .order_by("date").values_list("close"))
            if len(ohlc)==0:
                ohlc=deepcopy(bid)
            else:
                ohlc=np.concatenate([ohlc,bid],axis=0) #現在の価格を追加
            user_currency_chart+=user_coins_chart*ohlc

        user_chart=pd.Series(data=user_currency_chart.flatten(),name="user_chart").to_json()

    return chart_dates,user_chart


def get_pair_list(market:Market,currency:Currency):
    """
    取引所と通貨から,扱っている通貨ペアのリストを取得
    """

    pair_list=[]
    for pair in Pair.objects.filter(market=market):
        if currency.currency.casefold() in pair.pair.casefold():
            pair_list.append(pair)

    return pair_list