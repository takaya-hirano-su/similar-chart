from pathlib import Path
PARENT=str(Path(__file__).parent)
UTILS_PATH=str(Path(__file__).parent.parent)
PARAMS_PATH=str(Path(__file__).parent.parent.parent)
import sys
sys.path.append(PARAMS_PATH)
sys.path.append(UTILS_PATH)

import torch
from torch import Tensor,nn
from omegaconf import DictConfig
import numpy as np
import pandas as pd

from utils import make_batch,normalize
from .decoder import Decoder
from .encoder import Encoder
from params import DAYS,FUTURE_DAYS


class CryptAutoEncoder(nn.Module):

    def __init__(self,cfg:DictConfig):
        """
        入力したチャートの特徴から,似てる過去チャートを見つけるAI

        :param DictConfig cfg: パラメータが入った辞書

        ===以下はcfgのパラメタ===
        
        :param Dictconfig encoder: Encoderのパラメータが入った辞書
        :param DictConfig decoder: Decoderのパラメータが入った辞書
        """
        super(CryptAutoEncoder,self).__init__()
        self.encoder=Encoder(cfg.encoder)
        self.decoder=Decoder(cfg.decoder)

    def forward(self,x:Tensor):
        """
        特徴量の抽出＆復元する関数

        :param x: チャートの時系列データ
        :type Tensor: [batchsize x time_sequence x input_size]
        :return z: 特徴量
        :type z:Tenosr [batchsize x time_sequence x hidden_sizse]
        :return x_: 復元したデータ
        :type x_:Tensor [batchsize x time_sequence x input_size]
        """

        z=self.encoder.forward(x=x) #特徴量の抽出
        x_=self.decoder.forward(z=torch.flip(input=z,dims=[1])) #特徴量から復元. ただしzは時間方向に反転させる
        x_=torch.flip(input=x_,dims=[1]) #入力と反対の順番で復元するから, もう一回反転して入力の時間方向と同じにする

        return z,x_
    
    def loss_func(self,x:Tensor,label:Tensor):
        """
        損失関数の計算

        :param x: 復元したデータ
        :param label: 元のデータ
        :return int loss: 平均2乗誤差 (MSE)
        """

        criterion=torch.nn.MSELoss()
        loss=criterion(x,label)

        return loss
    
    @torch.no_grad()
    def encode(self,x:Tensor)->Tensor:
        """
        特徴量のみを出力する関数. 運用時に使う

        :param x : 入力の時系列データ
        :type x : Tensor[batchsize x timesequence x input_size]
        :return z: 特徴量
        :type z :Tensor[batchsize x timesequence x hidden_size]
        """
        return self.encoder(x)
    
    @torch.no_grad()
    def get_similar_chart(self,chart:pd.DataFrame,chart_past:pd.DataFrame,similar_chart_num:int=5):
        """
        似たチャートを選ぶ関数

        :param chart: 選択したチャート. 次元はohlcの4つと日付
        :type chart: pd.DataFrame [time_sequence x (open,high,low,close,date)]
        :param chart_past: 過去の時系列チャート. 次元はohlcの4つと日付
        :type chat_past: pd.DataFrame [time_sequence x (open,high,low,close,date)]
        :param int similar_chart_num: 上位何個のチャートを取るか
        """

        columns=["open","high","low","close"]

        chart_val=chart.loc[:,columns].values[np.newaxis,:,:] #バッチ方向に次元追加
        param_mean=np.mean(chart_val,axis=1)
        param_std=np.std(chart_val,axis=1)
        chart_val=normalize(chart_val) #標準化

        chart_past_val=chart_past.loc[:,columns].values
        chart_past_val=make_batch(values=chart_past_val)
        chart_past_val=normalize(chart_past_val)

        z=self.encode(Tensor(chart_val)).to("cpu").detach().numpy() #特徴量の抽出
        z_past=self.encode(Tensor(chart_past_val)).to("cpu").detach().numpy() #特徴量の抽出

        loss=(z_past[:,:,:]-z[:,:,:])**2 #2乗誤差を計算
        loss=np.mean(loss,axis=-1) #特徴次元方向に平均
        loss=np.mean(loss,axis=-1) #時間方向に平均

        best_idx=np.argmin(loss)

        ##上位からsimilar_chart_num個の似ているチャートを取得
        similar_charts=[] #似てるチャート
        similar_charts_scaled=[] #スケールを合わせた似てるチャート
        while len(similar_charts)<similar_chart_num:
            best_idx=np.argmin(loss)
            loss[best_idx]=np.inf
            
            similar_chart=chart_past.iloc[best_idx:best_idx+DAYS+FUTURE_DAYS] #FUTURE_DAYS日先まで見てみる

            is_near=False #もうすでに取ったところと近いところは省く
            for i in range(len(similar_charts)):
                similar_date=similar_charts[i]["date"].iloc[0]
                tmp_date=similar_chart["date"].iloc[0]
                if (similar_date-tmp_date).days<10:
                    is_near=True
                    break
            if is_near:
                continue
                    

            similar_charts.append(similar_chart.reset_index())

            val=similar_chart.loc[:,columns].values
            similar_chart_scaled=similar_chart.copy(deep=True)
            similar_chart_scaled.loc[:,columns]=(val-np.mean(val[:-FUTURE_DAYS],axis=0))/(1e-16+np.std(val[:-FUTURE_DAYS],axis=0))
            similar_chart_scaled.loc[:,columns]=similar_chart_scaled.loc[:,columns].values*(param_std+1e-16)+param_mean

            dt=chart["date"].iloc[0]-similar_chart["date"].iloc[0]
            similar_chart_scaled["date"]=similar_chart_scaled["date"].values+dt
            similar_charts_scaled.append(similar_chart_scaled.reset_index())

            
        ##

        return similar_charts,similar_charts_scaled