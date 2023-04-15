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

from crypto_auto_encoder import CryptAutoEncoder
from utils import make_batch,normalize,read_ohlc

CYAN="\033[36m"
RESETCOL="\033[0m"

@hydra.main(config_path="conf",config_name="main")
def main(cfg:DictConfig):

    ##AIモデルの準備
    crypt_auto_encoder=CryptAutoEncoder(cfg=cfg.crypto_auto_encoder)
    optimizer=torch.optim.Adam(params=crypt_auto_encoder.parameters(),lr=cfg.trainer.learning_rate)
    ##

    ##学習データの準備
    date_thr=(datetime.now()-timedelta(days=72)).date() #直近の72日はテストデータとして残す
    data_list=read_ohlc(date_thr=date_thr)
    train_data=np.array([])
    for data in data_list:
        batch_data=make_batch(values=data.loc[:,["open","high","low","close"]].values)
        if len(train_data)==0:
            train_data=batch_data
        else:
            train_data=np.concatenate([train_data,batch_data],axis=0)
    train_data=normalize(values=train_data) #学習データの標準化
    ##

    ##学習パラメータの準備
    mini_batch_size=cfg.trainer.mini_batch
    epoches=cfg.trainer.epoches
    save_interval=cfg.trainer.save_interval
    data_loader=DataLoader(
        dataset=torch.arange(start=0,end=train_data.shape[0],dtype=int),
        shuffle=True,
        drop_last=True,
        batch_size=mini_batch_size
    )
    model_param_dir=f"{PARENT}/model_param"
    if not os.path.exists(model_param_dir):
        os.makedirs(model_param_dir)
    ##

    ##学習ループ
    for epoch in range(epoches):

        print(f"{CYAN}***EPOCH[{RESETCOL}{epoch+1}{CYAN}] TRAINING START***{RESETCOL}")
        loss_epoch=[]

        for item in tqdm(data_loader):

            x=Tensor(train_data[item]) #入力のミニバッチ
            _,x_=crypt_auto_encoder.forward(x=x) #オートエンコーダーによる再構成
            loss:Tensor=crypt_auto_encoder.loss_func(x=x_,label=x) #損失関数の計算
            loss.backward() #誤差逆伝播でlossを流す
            optimizer.step() #重みの更新
            optimizer.zero_grad() #∂loss/∂Wのリセット

            loss_epoch.append(loss.item())

        print(f"{CYAN}***EPOCH[{RESETCOL}{epoch+1}{CYAN}]TRAINING DONE <AVG LOSS:{RESETCOL}{np.mean(loss_epoch)}{CYAN}>***{RESETCOL}\n")

        if (epoch+1)%save_interval==0:
            torch.save(crypt_auto_encoder.state_dict(),model_param_dir+f"\\param_epoch{epoch+1}.pth")
    ##        

if __name__=="__main__":
    main()