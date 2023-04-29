from pathlib import Path
PARENT=str(Path(__file__).parent)

from django.apps import AppConfig
from hydra import compose,initialize_config_dir
import torch
from apscheduler.schedulers.background import BackgroundScheduler


crypto_auto_encoder=None

class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):

        ##AIモデルの読み込み
        from .src.AI_model import CryptAutoEncoder

        global crypto_auto_encoder
        with initialize_config_dir(config_dir=f"{PARENT}/src/AI_model/conf"):
            cfg=compose(config_name="main.yaml")
        crypto_auto_encoder=CryptAutoEncoder(cfg=cfg.crypto_auto_encoder)
        crypto_auto_encoder.load_state_dict(torch.load(f"{PARENT}/src/AI_model/model_param/param_epoch500.pth"))
        print("=============")
        print(type(crypto_auto_encoder))
        print("=============")
        ##

        # update_ohlc() #起動時に一度OHLCレコ―ドを追加する(あれば) 

        # periodic_update_ohlc() ##OHLCテーブルの定期更新


def update_ohlc():
    from .models import Pair
    from .views import create_ohlc

    print("***update OHLC records***")

    ##OHLCレコードの追加(あれば)
    pairs=Pair.objects.all()
    for pair in pairs:
        create_ohlc(pair=pair)
    ##

def periodic_update_ohlc():
    """
    定期的(1日おき)にOHLCテーブルにレコードを追加する
    """

    scheduler=BackgroundScheduler()

    scheduler.add_job(update_ohlc,"interval",days=1)
    scheduler.start()

