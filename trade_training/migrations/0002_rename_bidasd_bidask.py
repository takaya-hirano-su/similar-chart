# Generated by Django 4.2 on 2023-04-22 10:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_alter_ohlc_date'),
        ('trade_training', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='BidAsd',
            new_name='BidAsk',
        ),
    ]