import pandas_datareader as pdr
import pandas as pd
import plotly
import plotly.graph_objects as go
import json
import os
from timestamp import Timestamp
from pandas_datareader._utils import RemoteDataError

class Invest(object):
    
    def __init__(self):
        self.wd_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.json_path = f"{self.wd_path}\\py"
        self.save_path = f"{self.wd_path}\\src\\invest"
        self.crypto_dict = self.set_crypto_dict()
        self.stock_dict = self.set_stock_dict()

    def set_crypto_dict(self):
        with open(f"{self.json_path}\\crypto.json" ,encoding="UTF-8") as crypto_json:
            crypto_dict = json.load(crypto_json)
        return crypto_dict

    def set_stock_dict(self):
        with open(f"{self.json_path}\\stock.json" ,encoding="UTF-8") as stock_json:
            stock_dict = json.load(stock_json)
        return stock_dict
    
    def mkdir(self):
        for crypto in self.crypto_dict:
            try:
                os.mkdir(f"{self.save_path}\\{crypto}")
            except FileExistsError:
                continue
        for stock in self.stock_dict:
            try:
                os.mkdir(f"{self.save_path}\\{stock}")
            except FileExistsError:
                continue

    def find_key(self, value):
        value = value.upper()
        for k,v in self.crypto_dict.items():
            for val in v:
                if value == val.upper():
                    return k
        for k,v in self.stock_dict.items():
            for val in v:
                if value == val.upper():
                    return k
        return value
    
    def get_data(self, value, start=None, stop=None):
        key = self.find_key(value)
        inv_df = pdr.get_data_yahoo(key, start, stop)
        print(inv_df)
        print(inv_df.index)
        html = self.to_candle(inv_df)
        return html

    def update(self):
        for crypto in self.crypto_dict:
            df = pdr.get_data_yahoo(crypto)
            df.to_csv(f"{self.save_path}\\{crypto}\\{crypto}.csv", encoding="UTF-8")
        for stock in self.stock_dict:
            df = pdr.get_data_yahoo(stock)
            df.to_csv(f"{self.save_path}\\{stock}\\{stock}.csv", encoding="UTF-8")

    def to_candle(self, dataframe):
        fig = go.Figure(data=[go.Candlestick(x=dataframe.index,
                                            open=dataframe["Open"],
                                            high=dataframe["High"],
                                            low=dataframe["Low"],
                                            close=dataframe["Close"])])
        fig.update_layout(xaxis_rangeslider_visible=False)
        raw_html = '<html><head><meta charset="utf-8" />'
        raw_html += '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script></head>'
        raw_html += '<body>'
        raw_html += plotly.offline.plot(fig, include_plotlyjs=False, output_type='div')
        raw_html += '</body></html>'
        return raw_html

if __name__ == "__main__":
    i = Invest()
    a = i.get_data("BTC")