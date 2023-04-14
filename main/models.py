from django.db import models

class Market(models.Model):
    """
    取引所のデータベース
    """
    market=models.CharField(max_length=50)


class Pair(models.Model):
    """
    取引所の扱っている銘柄のペア
    """
    market=models.ForeignKey(Market,on_delete=models.CASCADE) #CASCADE:関連づけられたオブジェクトと一緒に削除される
    pair=models.CharField(max_length=50)


class OHLC(models.Model):
    """
    仮想通貨のローソク足
    """

    market=models.ForeignKey(Market,on_delete=models.CASCADE)
    pair=models.ForeignKey(Pair,on_delete=models.CASCADE)

    is_train_data=models.BooleanField() #学習時に使ったデータかどうか
    open=models.IntegerField()
    high=models.IntegerField()
    low=models.IntegerField()
    close=models.IntegerField()
    datetime=models.DateTimeField()



