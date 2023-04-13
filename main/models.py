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


class CurrentOHLC(models.Model):
    """
    今のohlc
    """

    market=models.ForeignKey(Market,on_delete=models.CASCADE)
    pair=models.ForeignKey(Pair,on_delete=models.CASCADE)

    open=models.IntegerField()
    high=models.IntegerField()
    low=models.IntegerField()
    close=models.IntegerField()
    datetime=models.DateTimeField()


class TrainedOHLC(models.Model):
    """
    学習したohlc
    """

    market=models.ForeignKey(Market,on_delete=models.CASCADE)
    pair=models.ForeignKey(Pair,on_delete=models.CASCADE)

    open=models.IntegerField()
    high=models.IntegerField()
    low=models.IntegerField()
    close=models.IntegerField()
    datetime=models.DateTimeField()
