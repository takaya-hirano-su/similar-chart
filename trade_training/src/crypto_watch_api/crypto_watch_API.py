import requests


def get_BID_ASK(market:str,pair:str):
    """
    現在のBID(ユーザーの売値)とASK(ユーザーの買値)を取得する関数

    :param market: 対象の取引所
    :param pair: 対象の通貨ペア
    :return quote: bidとaskをキーに持つ辞書
    :type quote: dict {bid,ask}
    """

    base_url=f"https://api.cryptowat.ch/markets/{market}/{pair}/orderbook"
    response=requests.get(url=base_url).json()["result"]

    ask=response["asks"][0][0] #一番安いトレーダーの売り注文
    bid=response["bids"][0][0] #一番高いトレーダーの買い注文

    quote={
        "ask":ask,
        "bid":bid
    }

    return quote


if __name__=="__main__":
    print(get_BID_ASK(market="binance",pair="btcusdt"))