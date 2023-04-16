from pathlib import Path
PARENT=str(Path(__file__).parent)

from django.apps import AppConfig
from hydra.experimental import compose,initialize_config_dir
from .src.AI_model import CryptAutoEncoder
import torch


crypto_auto_encoder=None

class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        global crypto_auto_encoder

        ##AIモデルの読み込み
        with initialize_config_dir(config_dir=f"{PARENT}/src/AI_model/conf"):
            cfg=compose(config_name="main.yaml")
        crypto_auto_encoder=CryptAutoEncoder(cfg=cfg.crypto_auto_encoder)
        crypto_auto_encoder.load_state_dict(torch.load(f"{PARENT}/src/AI_model/model_param/param_epoch500.pth"))
        print("=============")
        print(type(crypto_auto_encoder))
        print("=============")
        ##

