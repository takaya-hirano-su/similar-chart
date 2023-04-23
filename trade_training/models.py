from django.db import models
from accounts.models import CustomUser
from main.models import Pair,Market

class Currency(models.Model):
    """
    通貨データベース\n
    JPYとかUSDTとか
    """
    currency=models.CharField(max_length=50)
    symbol=models.CharField(max_length=10,null=True)

    def __str__(self) -> str:
        return f"<Currency:{self.currency}>"

class BidAsk(models.Model):
    pair=models.ForeignKey(Pair,on_delete=models.CASCADE)
    bid=models.FloatField() #ユーザーの売値
    ask=models.FloatField() #ユーザーの買値
    datetime=models.DateTimeField(null=True,)

    def __str__(self):
        return f"<MARKET:{self.pair.market.market},PAIR:{self.pair.pair},BID:{self.bid},ASK:{self.ask}({self.datetime})>"

class UserNetAsset(models.Model):
    """
    ある取引所での総資産
    """
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    date=models.DateField(null=True)
    market=models.ForeignKey(Market,on_delete=models.CASCADE,null=True)
    
class UserCoin(models.Model):
    """
    その日付のときに,そのペアを何ロット持ってるか
    """
    net_asset=models.ForeignKey(UserNetAsset,on_delete=models.CASCADE)
    pair=models.ForeignKey(Pair,on_delete=models.CASCADE)
    lot=models.FloatField() #何ロット持ってるか

    def __str__(self):
        return f"<{self.net_asset.market.market}|PAIR:{self.pair.pair.upper()},LOT:{self.lot}({self.net_asset.date})>"

class UserCurrnecy(models.Model):
    """
    その日付のときに,その通貨をいくらもってるか
    """
    net_asset=models.ForeignKey(UserNetAsset,on_delete=models.CASCADE)
    currency=models.ForeignKey(Currency,on_delete=models.CASCADE)
    price=models.FloatField()

    def __str__(self):
        return f"<{self.net_asset.market.market}|{self.currency.currency}:{self.price}({self.net_asset.date})>"