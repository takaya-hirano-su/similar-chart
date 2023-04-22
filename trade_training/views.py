from django.shortcuts import render
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.db.models import Max

from datetime import datetime

from .src.crypto_watch_api import get_BID_ASK
from .forms import *
from main.models import Market,Pair
from accounts.models import CustomUser
from .models import BidAsk,UserNetAsset,UserCoin,UserCurrnecy,Currency

# Create your views here.
class TradeTrainingView(TemplateView):

    def get(self,request):  

        if not request.user.is_authenticated: #ログインしていなければsignup画面にリダイレクト
            return redirect(to="/accounts/signup")


        #--START 現在の気配値に関する処理
        ##初期状態の取引所と通貨ペアを取得
        initial_market=Market.objects.all()[0]
        initial_pair=Pair.objects.filter(market=initial_market)[0]
        ##

        now=datetime.now() #現在時刻

        quote_db=BidAsk.objects.filter(pair=initial_pair) #データベースの通貨ペアに対応する気配値を取得
        
        print(now,quote_db[0].datetime)
        if len(quote_db)==0: #まだ気配値を取得していないとき
            quote=get_BID_ASK(
                market=initial_market.market,
                pair=initial_pair.pair
                ) #今の気配値を取得
            
            quote_db_new=BidAsk(
                pair=initial_pair,
                bid=quote["bid"],ask=quote["ask"],
                datetime=now,
            )
            quote_db_new.save()

        elif (now-quote_db[0].datetime.replace(tzinfo=None)).seconds>60*10: #前回の更新から10分以上過ぎていたら更新
            quote=get_BID_ASK(
                market=initial_market.market,
                pair=initial_pair.pair
                ) #今の気配値を取得
            
            quote_db[0].datetime=now
            quote_db[0].ask=quote["ask"]
            quote_db[0].bid=quote["bid"]
            quote_db[0].save() #古いデータを更新

        quote=BidAsk.objects.filter(pair=initial_pair)[0] #更新後のデータを取得
        #--END 現在の気配値に関する処理


        #--START ユーザー資産情報に関する処理
        user_id=request.user.id 
        user=CustomUser.objects.filter(id=user_id)[0]
        net_asset_db=UserNetAsset.objects.filter(user=user) #ユーザーの総資産情報の取得
        if len(net_asset_db)==0: #総資産情報がないとき

            net_asset=UserNetAsset(
                user=user,
                date=now.date()
            )
            net_asset.save() #総資産情報の登録

            user_coin=UserCoin(
                net_asset=net_asset,
                pair=initial_pair,
                lot=0,
            )
            user_coin.save() #持ち仮想通貨情報の登録 (もってない登録)

            ##選択中の通貨を調べる
            for item in Currency.objects.all():
                print(item.currency,initial_pair.pair)
                if item.currency.casefold() in initial_pair.pair.casefold():
                    currency=item
                    break
            ##
            user_currency=UserCurrnecy(
                net_asset=net_asset,
                currency=currency,
                price=0
            )
            user_currency.save() #現在の通貨情報(日本円とかUSドルとか)の登録

        net_asset=UserNetAsset.objects.filter(user=user).order_by("date").last() #最新の情報を取得
        user_coin=UserCoin.objects.filter(net_asset=net_asset)[0]
        user_currency=UserCurrnecy.objects.filter(net_asset=net_asset)[0]
        #--END ユーザー資産情報に関する処理

        params={
            "market_pair_form":MarketPairForm(),
            "trade_form":TradeForm(),
            "quote":quote,
            "user_coin":user_coin,
            "user_currency":user_currency,
        }

        return render(request=request,template_name="trade_training/trade.html",context=params)
    
    def post(self,request):
        pass
