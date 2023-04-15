import os
import sys
from pathlib import Path
PARENT=str(Path(__file__).parent)
sys.path.append(PARENT)

from datetime import datetime,timedelta
import torch
from torch import Tensor
from torch.utils.data import DataLoader
from omegaconf import DictConfig
import hydra
import numpy as np
from tqdm import tqdm
from matplotlib import pyplot as plt

from crypto_auto_encoder import CryptAutoEncoder
from utils import make_batch,normalize,read_ohlc
from params import DAYS

CYAN="\033[36m"
RESETCOL="\033[0m"

@hydra.main(config_path="conf",config_name="main")
def main(cfg:DictConfig):
    """
    上手く学習できているか確認するコード
    """

    ##AIモデルの準備
    crypt_auto_encoder=CryptAutoEncoder(cfg=cfg.crypto_auto_encoder)
    crypt_auto_encoder.load_state_dict(torch.load(f"{PARENT}/model_param/param_epoch500.pth"))
    ##

    ##データベースからデータの取り出し
    date_thr=(datetime.now()).date()
    data_list=read_ohlc(date_thr=date_thr,is_train=False)
    ##

    pair_idx=3
    colmuns=["open","high","low","close"]
    test_data=data_list[pair_idx].iloc[-DAYS:].loc[:,colmuns]
    train_data=data_list[pair_idx].iloc[:-DAYS].loc[:,colmuns]

    similar_chart=crypt_auto_encoder.get_similar_chart(
        chart=test_data.values,chart_past=train_data.values
    )

    test_data_nrm=normalize(values=test_data.values[np.newaxis,:,:])[0] #標準化

    plt.plot(test_data_nrm[:,-1],label="test-chart")
    plt.plot(similar_chart[:,-1],label="similar-chart",alpha=0.5)
    plt.legend()
    plt.show()

if __name__=="__main__":
    main()