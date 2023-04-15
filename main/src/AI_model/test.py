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

    pair_idx=0
    bias=1
    colmuns=["open","high","low","close","date"]
    test_data=data_list[pair_idx].iloc[-DAYS-bias:-bias].loc[:,colmuns]
    train_data=data_list[pair_idx].iloc[:-DAYS].loc[:,colmuns]

    similar_charts,similar_charts_scaled=crypt_auto_encoder.get_similar_chart(
        chart=test_data,chart_past=train_data
    )

    fig=plt.figure(1)
    ax=fig.add_subplot(1,1,1)
    ax.plot(test_data["date"].values,test_data["close"].values,label="test-chart")

    fig2,ax2=plt.subplots(nrows=2,ncols=3)
    ax2=ax2.flatten()
    
    for i in range(5):
        ax.plot(similar_charts_scaled[i]["date"].values,
                similar_charts_scaled[i]["close"].values,
                label=f"similar-chart.No{i+1}",alpha=0.5**(i+1)
                )
        ax2[i].plot(similar_charts[i]["date"].values,
                similar_charts[i]["close"].values,
                label=f"similar-chart.No{i+1}",alpha=0.9**(i+1)
                )
        ax.legend()
        ax2[i].legend()
    plt.show()
    

if __name__=="__main__":
    main()