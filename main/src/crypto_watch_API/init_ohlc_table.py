from pathlib import Path
import sys
ROOT_PATH=str(Path(__file__).parent.parent.parent.parent)
print(ROOT_PATH)
sys.path.append(ROOT_PATH)

import psycopg2
from datetime import datetime,timedelta
import pandas as pd
import re

from crypto_watch_API import get_chart
from envs import *

def make_querry_from_pandas(values:pd.DataFrame,pair_id):

    querry="INSERT INTO main_ohlc (is_train_data,open,high,low,close,date,pair_id) VALUES"
    for idx,row in values.iterrows():
        #print(row)
        record=f"({False},{row['open']},{row['high']},{row['low']},{row['close']},'{(row['datetime'].date())}',{pair_id}),"
        querry+=record

    querry=re.sub(",$",";",querry)

    return querry


def main():
    """
    一番初めにデータベースにローソク足を登録するコード
    """
    now=datetime.now()
    delta=timedelta(days=365*10)
    after=now-delta

    # print(repr(now))
    # exit(1)

    conn=psycopg2.connect(
        host=host,
        user=user,
        database=database,
        password=password
    )

    # print("Database is connected.")
    # exit(1)

    with conn:
        with conn.cursor() as cursor:

            #--データベースから,market(取引所)とpair(通貨ペア)のリストを取得
            querry="SELECT market_id,pair,id FROM main_pair;"
            cursor.execute(query=querry)
            pair_list=cursor.fetchall()

            querry="SELECT id,market FROM main_market;"
            cursor.execute(query=querry)
            market_list=cursor.fetchall()

            pairs=[]
            for pair_item in pair_list:
                pair_name=pair_item[1]
                for market_item in market_list:
                    if market_item[0]==pair_item[0]:
                        market_name=market_item[1]
                        break
                pairs.append({"market":market_name,"pair":pair_name,"pair_id":pair_item[2]})
            #--
            
            for item in pairs:
                chart=get_chart(
                    market=item["market"],pair=item["pair"],
                    before=now,after=after
                )

                querry=make_querry_from_pandas(
                    values=chart,pair_id=item["pair_id"]
                )
                
                cursor.execute(querry) #レコードの追加

        conn.commit()

if __name__=="__main__":
    main()