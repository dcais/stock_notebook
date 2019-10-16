import tushare as ts
import pandas as pd
import json
import re
from os.path import abspath, join, dirname


class TsStock:
    index = {'上证综指': '000001.SH',
             '深证成指': '399001.SZ',
             '沪深300': '000300.SH',
             '创业板指': '399006.SZ',
             '上证50': '000016.SH',
             '中证500': '000905.SH',
             '中小板指': '399005.SZ',
             '上证180': '000010.SH'}

    def __init__(self):
        config_path = join(abspath(dirname(__file__)), '../config.json')
        with open(config_path) as json_file:
            conf_dict = json.load(json_file)
            conf_tushare_token = conf_dict['tushareToken']
        ts.set_token(conf_tushare_token)
        self.pro = ts.pro_api()
        df = self.pro.stock_basic(exchange='', list_status='L')
        self.stock_df = df

    def get_stock_info(self, keyword):

        code = ''
        symbol = ''
        name = ''
        isIndex = False

        if keyword in TsStock.index:
            code = TsStock.index[keyword]
            name = keyword
            symbol = code
            isIndex = True
        else:
            code_df = self.stock_df
            if re.match(r'\d{6}', keyword):
                code_df.index = code_df['symbol']
            else:
                code_df.index = code_df['name']
            code = code_df.loc[keyword, 'ts_code']
            symbol = code_df.loc[keyword, 'symbol']
            name = code_df.loc[keyword, 'name']

        return {
            "code": code,
            "symbol": symbol,
            "name": name,
            "is_index": isIndex
        }

    def get_daily_data(self, keyword, start_date='', end_date=''):
        stockInfo = self.get_stock_info(keyword)
        df = None
        if (stockInfo['is_index']):
            df = self.pro.index_daily(ts_code=stockInfo['code'], start_date=start_date, end_date=end_date)
            df.index = pd.to_datetime(df.trade_date)
            df = df.sort_index()
        else:
            df = ts.pro_bar(ts_code=stockInfo['code'], adj='qfq', start_date=start_date, end_date=end_date)
            df_basic = self.pro.daily_basic(ts_code=stockInfo['code'], start_date=start_date, end_date=end_date)
            df.index = pd.to_datetime(df.trade_date)
            df = df.sort_index()
            df_basic.index = pd.to_datetime(df_basic.trade_date)
            df_basic = df_basic.sort_index()
            df['turnover_rate'] = df_basic['turnover_rate']
            df['volume_ratio'] = df_basic['volume_ratio']

        return df
