from django.shortcuts import render
from django.views.generic import TemplateView
from django.shortcuts import redirect

from datetime import datetime
import json

from .forms import MarketCurrencyForm,DepositWithdrawForm,custom_valid
from main.models import Market,Pair 
from accounts.models import CustomUser
from trade_training.models import UserNetAsset,Currency,UserCurrnecy,UserCoin,BidAsk
from trade_training.views import init_net_asset,create_net_asset,init_update_quote,get_currency_list


# Create your views here.
class DepositView(TemplateView):

    def get(self,request):

        if not request.user.is_authenticated: #ログインしていなければsignup画面にリダイレクト
            return redirect(to="/accounts/signup")
        
        now=datetime.now() #現在時刻
        
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

        #ユーザーの資産情報の取得  
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
        #print(user_coins)

        params={
            "market_currency_form":MarketCurrencyForm(),
            "deposit_withdraw_form":DepositWithdrawForm(),
            "user_currency":user_currency,
            "user_coins":user_coins,
            "error_msg":"",
        }

        return render(request=request,template_name="deposit/deposit.html",context=params)
    

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
        print(request_post)    
        market_currency_form=MarketCurrencyForm(request_post)
        market_currency_form.fields["currency"].choices=[(item.currency,item.currency) for item in currency_list]
        market_currency_form.base_fields["currency"].choices=[(item.currency,item.currency) for item in currency_list]


        #現在の資産情報の有無
        is_current=True if not len(UserNetAsset.objects.filter(user=user,date=now.date(),market=market))==0 else False
        if not is_current:
            create_net_asset(user=user,now=now,market=market) #今日の情報がないときは新たに作成


        #ユーザーの資産情報の取得  
        user=CustomUser.objects.get(id=request.user.id)
        net_asset=UserNetAsset.objects.filter(user=user,market=market).order_by("date").last()
        

        #確定ボタンが押されたら,入金or出金
        error_msg=""
        if request_post["is_commit"]=="True":
            if request_post["action"]=="deposit":
                deposit(net_asset=net_asset,currency=currency,price=float(request_post["price"]))
            
            elif request_post["action"]=="withdraw":
                user_currency=UserCurrnecy.objects.get(net_asset=net_asset,currency=currency)
                error_msg=custom_valid(price=float(request_post["price"]),user_currency=user_currency) #残高以上のお金を引き出そうとしていないかチェック
                
                if error_msg=="": #問題なければ引き出す
                    withdraw(net_asset=net_asset,currency=currency,price=float(request_post["price"]))
        
        
        #最新の情報を取得
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
        

        request_post["price"]=0
        request_post["is_commit"]="False"
        params={
            "market_currency_form":market_currency_form,
            "deposit_withdraw_form":DepositWithdrawForm(request_post),
            "user_currency":user_currency,
            "user_coins":user_coins,
            "error_msg":error_msg,
        }

        return render(request=request,template_name="deposit/deposit.html",context=params)

def deposit(net_asset:UserNetAsset,currency:Currency,price:float):
    """
    入金処理

    :param net_asset: 現在の総資産
    :param currency: 選択中の通貨
    :param price: 金額
    """

    user_currency=UserCurrnecy.objects.get(net_asset=net_asset,currency=currency)
    user_currency.price+=price
    user_currency.save()

def withdraw(net_asset:UserNetAsset,currency:Currency,price:float):
    """
    出金処理

    :param net_asset: 現在の総資産
    :param currency: 選択中の通貨
    :param price: 金額
    """
    user_currency=UserCurrnecy.objects.get(net_asset=net_asset,currency=currency)
    user_currency.price-=price
    user_currency.save()
    
