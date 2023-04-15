import pandas as pd
import numpy as np
import psycopg2


def to_csv():
    """
    学習時はGPU付きのPCで学習させたい.

    データベースの学習データはcsvにして置く用の関数.
    """

    con=psycopg2.connect(
        host="localhost",
        user="postgres",
        password="xe7z76fr",
        database="similar_chart",
    )



    with con:
        with con.cursor() as cursor:
            
            query="SELECT * FROM main_pair;"
            cursor.execute(query=query)
            pair=cursor.fetchall()
            print(pair)

            query="SELECT id,open,high,low,close FROM main_ohlc WHERE pair_id=1 ORDER BY date;"
            cursor.execute(query=query)
            ohlc=cursor.fetchall()
            print(ohlc)

        con.commit()

if __name__=="__main__":
    to_csv()