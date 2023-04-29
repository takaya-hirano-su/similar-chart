import sys
from pathlib import Path
param_path=str(Path(__file__).parent.parent.parent)
root_path=str(Path(__file__).parent.parent.parent.parent)
sys.path.append(param_path)
sys.path.append(root_path)

import pandas as pd
import numpy as np
import psycopg2
from datetime import date

from params import DAYS
from envs import *


def to_tuple_form(values:np.ndarray):
    """
    numpy配列をtuple形式の文字列に変形する
    """
    tuple_form="("
    for val in values[:-1]:
        tuple_form+=f"{val},"
    tuple_form+=str(values[-1])
    tuple_form+=")"

    return tuple_form


def read_ohlc(date_thr:date,is_train=True)->list:
    """
    テーブルから読みだす関数

    :param date_thr: これ以前のデータを読みだす
    :param bool is_train: Trueのとき,データベースのis_train_dataがTrueになる
    :retrun data_list: 通貨ペアごとのDataFrameが返り値
    :type data_list: list [DataFrame(pair1),DataFrame(pair2),...]
    """

    con=psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=database,
    )


    colmuns=["id","is_train_data","open","high","low","close","date"]
    data_list=[] #通貨ペアごとのデータ
    # date_thr=(datetime.now()-timedelta(days=30)).date() #これ以前のデータを使う
    with con:
        with con.cursor() as cursor:
            
            query="SELECT id FROM main_pair;"
            cursor.execute(query=query)
            pair_ids=cursor.fetchall()
            # print(pair_ids)

            ##全てのis_train_dataをfalse
            if is_train:
                query=f"UPDATE main_ohlc SET is_train_data=FALSE;"
                cursor.execute(query=query)
            ##

            for pair_id in pair_ids:
                query=f"SELECT id,is_train_data,open,high,low,close,date FROM main_ohlc WHERE pair_id={pair_id[0]} AND date<'{str(date_thr)}' ORDER BY date;"
                cursor.execute(query=query)
                ohlc=pd.DataFrame(cursor.fetchall(),columns=colmuns)

                data_list.append(ohlc)

                if is_train:
                    data_ids=to_tuple_form(ohlc["id"].values)
                    query=f"UPDATE main_ohlc SET is_train_data=TRUE WHERE id in {data_ids} AND is_train_data=FALSE;" #学習用に取得したデータにチェックつける
                    cursor.execute(query=query)

        con.commit()

    return data_list



def make_batch(values:np.ndarray,batch_sequence:int=DAYS):
    """
    1本の時系列データをバッチ形式に変換する

    :param values:1列の時系列データ
    :type values: numpy.ndarray [time_sequence x input_size]
    :param int batch_sequence: 1つのバッチデータにおける時系列の長さ
    :return batch: バッチ形式にしたデータ
    :type batch: numpy.ndarray [batchsize x DAYS x input_size]
    """

    batch=[]
    length,_=values.shape
    for i in range(length-batch_sequence+1):
        batch.append(values[i:i+batch_sequence])

    return np.array(batch)


def normalize(values:np.ndarray):
    """
    時系列方向に標準化する関数. make_batchした後のデータに使う

    :param values: バッチ形式にした時系列データ
    :type values: numpy.ndarray [batchsize x DAYS x input_size]
    :return values_nrm: 標準化後のバッチ形式にしたデータ
    :type values_nrm: numpy.ndarray [batchsize x DAYS x input_size]
    """

    mean=np.mean(values,axis=1) #時系列方向の平均
    std=np.std(values,axis=1) #時系列方向の標準偏差

    mean=mean[:,np.newaxis,:] #時系列方向に次元追加
    std=std[:,np.newaxis,:]   #時系列方向に次元追加

    values_nrm=(values-mean)/(std+1e-16) #標準化 (平均を0,標準偏差を1にする)

    return values_nrm