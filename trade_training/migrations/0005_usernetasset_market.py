# Generated by Django 4.2 on 2023-04-23 05:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_alter_ohlc_date'),
        ('trade_training', '0004_currency_symbol'),
    ]

    operations = [
        migrations.AddField(
            model_name='usernetasset',
            name='market',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.market'),
        ),
    ]
