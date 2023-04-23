from django.shortcuts import render
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.db.models import Max

from datetime import datetime
from copy import deepcopy

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
        initial_currency=get_currency(pair=initial_pair)
        ##

        now=datetime.now() #現在時刻

        init_update_quote(
            market=initial_market,
            pair=initial_pair,now=now
            ) #気配値情報の新規登録or更新

        quote=BidAsk.objects.get(pair=initial_pair) #更新後のデータを取得
        #--END 現在の気配値に関する処理


        #--START ユーザー資産情報に関する処理
        user_id=request.user.id 
        user=CustomUser.objects.get(id=user_id)
        is_user_asset=True if not len(UserNetAsset.objects.filter(user=user,market=initial_market))==0 else False
        if not is_user_asset: #総資産情報がないときは初期化
            init_net_asset(user=user,now=now,market=initial_market)

        net_asset=UserNetAsset.objects.filter(user=user,market=initial_market).order_by("date").last() #最新の情報を取得
        user_coin=UserCoin.objects.get(net_asset=net_asset,pair=initial_pair)
        user_currency=UserCurrnecy.objects.get(net_asset=net_asset,currency=initial_currency)
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

        now=datetime.now() #現在時刻

        user=CustomUser.objects.get(id=request.user.id) #ユーザー情報
        
        market=Market.objects.get(market=request.POST["market"]) #formで選択したmarket
        choices=[item for item in Pair.objects.filter(market=market)] #選択したmarket取り扱いのある通貨ペア
        pair=Pair.objects.get(pair=request.POST["pair"]) #formで選択した通貨ペア


        #取り扱っていない通貨ペアが選択されていたら,扱っているものに書き換える
        request_post=request.POST.copy()
        if not pair in choices: 
            request_post["pair"]=choices[0].pair
            pair=choices[0]
        market_pair_form=MarketPairForm(request_post)
        market_pair_form.fields["pair"].choices=[(item.pair,item.pair) for item in choices]
        market_pair_form.base_fields["pair"].choices=[(item.pair,item.pair) for item in choices]


        currency=get_currency(pair=pair) #今選択中の通貨


        #気配値情報の新規登録or更新
        init_update_quote(market=market,pair=pair,now=now) 
        quote=BidAsk.objects.get(pair=pair) #更新後のデータを取得


        #資産情報の有無
        is_user_asset=True if not len(UserNetAsset.objects.filter(user=user,market=market))==0 else False
        if not is_user_asset: #情報が1つもないときは0で初期化
            init_net_asset(user=user,now=now,market=market)

        #現在の資産情報の有無
        is_current=True if not len(UserNetAsset.objects.filter(user=user,date=now.date(),market=market))==0 else False
        if not is_current:
            create_net_asset(user=user,now=now,market=market) #今日の情報がないときは新たに作成

        #ユーザーの資産情報の取得  
        user=CustomUser.objects.get(id=request.user.id)
        net_asset=UserNetAsset.objects.filter(user=user,market=market).order_by("date").last() #最新の情報を取得
        user_coin=UserCoin.objects.get(net_asset=net_asset,pair=pair)
        user_currency=UserCurrnecy.objects.get(net_asset=net_asset,currency=currency)

        if request_post["is_commit"]=="True": #確定ボタンが押された時だけ,売買の処理をする
            if request_post["action"]=="buy":
                action_buy(
                    user_coin=user_coin,user_currency=user_currency,
                    ask=quote.ask,lot=float(request_post["lot"])
                    )
            elif request_post["action"]=="sell":
                action_sell(
                    user_coin=user_coin,user_currency=user_currency,
                    bid=quote.bid,lot=float(request_post["lot"])
                    )
            
        user_coin=UserCoin.objects.get(net_asset=net_asset,pair=pair)
        user_currency=UserCurrnecy.objects.get(net_asset=net_asset,currency=currency)

        request_post["lot"]=0.0
        request_post["is_commit"]="False"
        params={
            "market_pair_form":market_pair_form,
            "trade_form":TradeForm(request_post),
            "quote":quote,
            "user_coin":user_coin,
            "user_currency":user_currency,
        }

        return render(request=request,template_name="trade_training/trade.html",context=params)


def init_update_quote(market:Market,pair:Pair,now:datetime):
    """
    気配値情報を更新or新規登録する関数

    :param market: 選択した取引所
    :type Market: Models {market}
    :param pair: 選択した通貨ペア
    :param Pair: Models {Market,pair}
    :param datetime now: 今の時間
    """

    quote_db=BidAsk.objects.filter(pair=pair) #データベースの通貨ペアに対応する気配値を取得
        
    if len(quote_db)==0: #まだ気配値を取得していないとき
        quote=get_BID_ASK(
            market=market.market,
            pair=pair.pair
            ) #今の気配値を取得
        
        quote_db_new=BidAsk(
            pair=pair,
            bid=quote["bid"],ask=quote["ask"],
            datetime=now,
        )
        quote_db_new.save()

    elif (now-quote_db[0].datetime.replace(tzinfo=None)).seconds>60*10: #前回の更新から10分以上過ぎていたら更新
        quote=get_BID_ASK(
            market=market.market,
            pair=pair.pair
            ) #今の気配値を取得
        
        quote_db[0].datetime=now
        quote_db[0].ask=quote["ask"]
        quote_db[0].bid=quote["bid"]
        quote_db[0].save() #古いデータを更新

def init_net_asset(user:CustomUser,market:Market,now:datetime):
    """
    資産情報の初期化

    :param user: ユーザー情報
    :type user: CustomUser
    :param market:選択中の取引所
    :param datetime now: 現在時刻
    """
    #総資産情報の登録
    net_asset=UserNetAsset(
        user=user,
        date=now.date(),
        market=market
    )
    net_asset.save() 

    #持ち仮想通貨情報の登録 (0コイン持ってるとして登録)
    for pair in Pair.objects.all():
        user_coin=UserCoin(
            net_asset=net_asset,
            pair=pair,
            lot=0,
        )
        user_coin.save() 

    #通貨(日本円とかUSドルとか)の登録
    for currency in Currency.objects.all():
        user_currency=UserCurrnecy(
            net_asset=net_asset,
            currency=currency,
            price=0
        )
        user_currency.save() #現在の通貨情報(日本円とかUSドルとか)の登録

def create_net_asset(user:CustomUser,market:Market,now:datetime):
    """
    現在の資産情報を登録する関数
    """

    net_asset_latest=UserNetAsset.objects.filter(user=user,market=market).order_by("date").last() #今までの最新のデータを取得

    #現在のデータを登録
    net_asset_current=UserNetAsset(user=user,date=now.date(),market=market) 
    net_asset_current.save()

    #--今までの中で最新だった情報をコピーして,現在の持ちコイン情報とする
    user_coins_current=UserCoin.objects.filter(net_asset=net_asset_latest) 
    for user_coin_current in user_coins_current:
        user_coin_current.net_asset=net_asset_current
        user_coin_current.id=None
        user_coin_current.save()
    #--

    #--今までの中で最新だった情報をコピーして,現在の持ち通貨情報とする
    user_currencies_current=UserCurrnecy.objects.filter(net_asset=net_asset_latest)
    for user_currency_current in user_currencies_current:
        user_currency_current.net_asset=net_asset_current
        user_currency_current.id=None
        user_currency_current.save()
    #--

def get_currency(pair:Pair)->Currency:
    """
    選択中の通貨ペアからどの通貨を扱っているか取得する関数

    :param pair: 選択中の通貨ペア
    :type pair: Pair
    :return currency: 扱っている通貨(日本円とかUSドルとか)
    :type currency: Currency
    """

    pair_name=pair.pair
    for currency in Currency.objects.all():
        if currency.currency.casefold() in pair_name.casefold():
            return currency

def action_buy(user_coin:UserCoin,user_currency:UserCurrnecy,ask:float,lot:float):
    """
    買ったときの処理

    :param user_coin:更新前の持ちコイン
    :param user_currency: 更新前の持ち通貨
    :param ask: 今のユーザーの買値
    :param lot: 何コイン買うか
    """

    crypto_price=lot*ask
    user_currency.price-=crypto_price #買った分だけ持ち通貨をマイナス
    user_currency.save()

    user_coin.lot+=lot #買った分だけコインをプラス
    user_coin.save()

def action_sell(user_coin:UserCoin,user_currency:UserCurrnecy,bid:float,lot:float):
    """
    売ったときの処理

    :param user_coin:更新前の持ちコイン
    :param user_currency: 更新前の持ち通貨
    :param bid: 今のユーザーの売値
    :param lot: 何コイン売るか
    """

    crypto_price=lot*bid
    user_currency.price+=crypto_price #売った分だけ持ち通貨をプラス
    user_currency.save()

    user_coin.lot-=lot #売った分だけコインをマイナス
    user_coin.save()