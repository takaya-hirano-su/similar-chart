import torch
from torch import Tensor,nn
from omegaconf import DictConfig

from .decoder import Decoder
from .encoder import Encoder


class CryptAutoEncoder(nn.Module):

    def __init__(self,cfg:DictConfig):
        """
        入力したチャートの特徴から,似てる過去チャートを見つけるAI

        :param DictConfig cfg: パラメータが入った辞書

        ===以下はcfgのパラメタ===
        :param Dictconfig encoder: Encoderのパラメータが入った辞書
        :param DictConfig decoder: Decoderのパラメータが入った辞書
        """

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