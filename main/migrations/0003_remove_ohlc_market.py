# Generated by Django 4.2 on 2023-04-14 07:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_ohlc_remove_trainedohlc_market_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ohlc',
            name='market',
        ),
    ]
