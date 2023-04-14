from django.db import models


class Market(models.Model):
    """
    取引所のデータベース
    """
    market=models.CharField(max_length=50)

    def __str__(self):
        return f"<Market:id{self.id},{self.market}>"


class Pair(models.Model):
    """
    取引所の扱っている銘柄のペア
    """
    market=models.ForeignKey(Market,on_delete=models.CASCADE) #CASCADE:関連づけられたオブジェクトと一緒に削除される
    pair=models.CharField(max_length=50)

    def __str__(self):
        return f"<Pair:id:{self.id}, market:{self.market.market}, pair:{self.pair}>"


class OHLC(models.Model):
    """
    仮想通貨のローソク足
    """

    pair=models.ForeignKey(Pair,on_delete=models.CASCADE) #取引所と通貨ペアの情報

    is_train_data=models.BooleanField() #学習時に使ったデータかどうか
    open=models.IntegerField()
    high=models.IntegerField()
    low=models.IntegerField()
    close=models.IntegerField()
    date=models.DateField(null=True)

    def __str__(self):
        return f"<ohlc market:{self.pair.market.market}, pair:{self.pair.pair} ({self.date})>"



