import tushare as ts
import pandas as pd
import re
import mysqlx
import json
from os.path import abspath, join, dirname
import datetime
from datetime import date

connection_string = {
}

client_options = {
    'pooling': {
        "max_size": 10,
        "max_idle_time": 30000
    }
}


def convert_to_underline(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


class Stock:
    x_client = None
    stock_df = None

    def __init__(self):
        config_path = join(abspath(dirname(__file__)), '../config.json')
        with open(config_path) as json_file:
            conf_dict = json.load(json_file)
            conf_mysql = conf_dict['mysql']
            conf_tushare_token = conf_dict['tushareToken']

        ts.set_token(conf_tushare_token)
        self.pro = ts.pro_api()
        df = self.pro.stock_basic(exchange='', list_status='L')
        self.stock_df = df

        self.x_client = mysqlx.get_client(conf_mysql, client_options)

    def get_schema(self):
        session = self.x_client.get_session()
        schema = session.get_schema('stock')
        return (session, schema)

    def get_stock_info(self, keyword):
        code = ''
        symbol = ''
        name = ''

        code_df = self.stock_df
        if re.match(r'\d{6}\.', keyword):
            code_df.index = code_df['ts_code']
        elif re.match(r'\d{6}', keyword):
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
        }

    def get_daily_data(self, keyword, start_date='', end_date=''):
        session, schema = self.get_schema();
        stock_info = self.get_stock_info(keyword)
        col = schema.get_collection('stock_x_split_adjusted_daily')
        query = "tsCode = :tscode"
        params = {
            "tscode": stock_info['code']
        }
        if start_date != '':
            query += " and tradeDate >= :start_date"
            params['start_date'] = pd.to_datetime(start_date).strftime("%Y-%m-%d")
        if end_date != '':
            query += ' and tradeDate <= :end_date'
            params['end_date'] = pd.to_datetime(start_date).strftime("%Y-%m-%d")

        docs = col.find(query) \
            .bind(params) \
            .execute()

        dailyDatas = docs.fetch_all()

        if len(dailyDatas) == 0:
            return None

        variables = dailyDatas[0].keys()
        names = []
        for v in variables:
            names.append(convert_to_underline(v))
        # print(names)
        df = pd.DataFrame([[getattr(i, j) for j in variables] for i in dailyDatas], columns=names)
        df = df[['trade_date', 'ts_code', 'low', 'vol', 'high', 'open', 'pre_close', 'close', 'amount', 'pct_chg']]
        df['trade_date'] = df.trade_date.str[:10]

        df.index = pd.to_datetime(df.trade_date)
        df = df.sort_index()
        session.close()
        return df

    def get_stock_basic(self, keyword, start_date, end_date):
        session, schema = self.get_schema()
        col = schema.get_collection('stock_x_daily_basic')
        stock_info = self.get_stock_info(keyword)
        query = "tsCode = :tscode"
        params = {
            "tscode": stock_info['code']
        }
        if start_date != '':
            query += " and tradeDate >= :start_date"
            params['start_date'] = pd.to_datetime(start_date).strftime("%Y-%m-%d")
        if end_date != '':
            query += ' and tradeDate <= :end_date'
            params['end_date'] = pd.to_datetime(start_date).strftime("%Y-%m-%d")

        docs = col.find(query) \
            .bind(params) \
            .execute()

        dailyDatas = docs.fetch_all()

        if len(dailyDatas) == 0:
            return None

        variables = dailyDatas[0].keys()
        names = []
        for v in variables:
            names.append(convert_to_underline(v))
        # print(names)
        df = pd.DataFrame([[getattr(i, j) for j in variables] for i in dailyDatas], columns=names)
        df = df[['trade_date', 'ts_code', 'low', 'vol', 'high', 'open', 'pre_close', 'close', 'amount', 'pct_chg']]
        df['trade_date'] = df.trade_date.str[:10]
        df.index = pd.to_datetime(df.trade_date)
        df = df.sort_index()
        session.close()
        return df

    def index_weight(self, index_code):
        today = date.today()

        begin = today.replace(day=1)
        df = self.pro.index_weight(index_code=index_code, start_date=begin.strftime('%Y%m%d'))

        if len(df) == 0:
           end = today.replace(day=1) - datetime.timedelta(1)
           begin = end.replace(day=1)
           df = self.pro.index_weight(index_code=index_code, start_date=begin.strftime('%Y%m%d'), end_date=end.strftime('%Y%m%d'))

        df = df.drop_duplicates(["con_code"], keep="last")
        df['ts_code'] = df['con_code']
        df.index = df["ts_code"]
        return df

    def get_hs_300(self):
        return self.index_weight('399300.SZ')

    def get_zz_500(self):
        return self.index_weight('000905.SH')

    def get_sz_50(self):
        return self.index_weight("000016.SH")

    def get_concept_detail(self):
        session, schema = self.get_schema();
        col = schema.get_collection('stock_x_concept_detail')
        query = "true"
        docs = col.find(query) \
            .execute()

        concept_details = docs.fetch_all()

        if len(concept_details) == 0:
            return None

        variables = ['code', 'name', 'tsCode', 'conceptName']
        print(variables)
        names = []
        for v in variables:
            names.append(convert_to_underline(v))
        # print(names)
        df = pd.DataFrame([[getattr(i, j) for j in variables] for i in concept_details], columns=names)

        df.index = df.ts_code
        df = df.sort_index()
        session.close()
        return df

