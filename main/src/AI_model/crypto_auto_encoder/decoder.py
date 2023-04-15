import torch
from torch import nn,Tensor
from omegaconf import DictConfig


class Decoder(nn.Module):
    def __init__(self,cfg:DictConfig):
        """
        encoderで抽出した特徴から,元のチャートを復元するクラス

        :param DictConfig cfg: モデルパラメータが格納された辞書

        ===以下はcfgのパラメータ===

        :param int input_size: 入力次元 (encoderのhidden_sizeと一致)
        :param int output_size: 出力次元 (enocderのinput_sizeと一致)
        :param int hidden_size: 隠れ層の次元
        :param int hidden_layer_num: 隠れ層の層数
        """
        super(Decoder,self).__init__()

        self.decoder=nn.LSTM(
            input_size=cfg.input_size,
            hidden_size=cfg.hidden_size,
            num_layers=cfg.hidden_layer_num,
            batch_first=True,
        ) #中間層

        self.out_layer=nn.Linear(
            in_features=cfg.hidden_size,
            out_features=cfg.output_size
        ) #出力層


    def forward(self,z:Tensor)->Tensor:
        """
        encoderで抽出した特徴量から元のデータを復元する

        :param z: encoder抽出した特徴量. 時系列方向は反転しておく
        :type z: Tensor [batchsize x time_sequence x hidden_size]
        :return x: 復元した元の時系列データ
        :type x: Tensor [batchsize x time_sequence x output_size]
        """

        x,(_,_)=self.decoder(z)
        x=self.out_layer(x)
        return x

