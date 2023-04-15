import torch
from torch import Tensor,nn
from omegaconf import DictConfig


class Encoder(nn.Module):
    def __init__(self,cfg:DictConfig):
        """
        過去チャートから特徴量を抽出するモデル

        :param DictConfig cfg: モデルパラメータが格納されている辞書

        ===以下はcfg内のパラメータ===

        :param int input_size: 入力次元数
        :param int hidden_size: 隠れ層の次元数 (これが特徴量の次元数になる)
        :param int hidden_layer_num: 隠れ層の層数 (LSTMの層数)
        """
        super(Encoder,self).__init__()
        self.encoder=nn.LSTM(
            input_size=cfg.input_size,
            hidden_size=cfg.hidden_size,
            num_layers=cfg.hidden_layer_num,
            batch_first=True
        )

    def forward(self,x:Tensor)->Tensor:
        """
        過去チャートから特徴抽出

        :param x: チャートの時系列データ
        :type x: Tensor [batch_size x time_sequence x input_dim]
        :return z: 抽出された特徴量 
        :type z: Tensor[batch_size x time_sequence x hidden_size]
        """
        z,(_,_)=self.encoder(x)
        return z