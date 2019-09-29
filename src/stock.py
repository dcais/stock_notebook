import tushare as ts
import pandas as pd
import re
import mysqlx

connection_string = {
    'host': 'localhost',
    'port': 33160,
    'user': 'stock',
    'password': 'aRmbZH9dx9k6TzRB'
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
    token = '36d50a0386e9066b5c79c2de58ea2d3a9b980020041adc910f76bfc7'
    x_client = None

    def __init__(self):
        ts.set_token(Stock.token)
        self.pro = ts.pro_api()
        df = self.pro.stock_basic(exchange='', list_status='L')
        self.stock_df = df
        self.x_client = mysqlx.get_client(connection_string, client_options)

    def get_schema(self):
        session = self.x_client.get_session()
        schema = session.get_schema('stock')
        return (session,schema)

    def get_stock_info(self, keyword):
        code = ''
        symbol = ''
        name = ''

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
        }

    def get_daily_data(self, keyword, start_date = '' , end_date = '' ):
        session,schema = self.get_schema();
        stock_info = self.get_stock_info(keyword)
        col = schema.get_collection('stock_x_split_adjusted_daily')
        query = "tsCode = :tscode"
        params = {
            "tscode" : stock_info['code']
        }
        if start_date != '':
            query += " and tradeDate >= :start_date"
            params['start_date'] = pd.to_datetime(start_date).strftime("%Y-%m-%d")
        if end_date != '':
            query += ' and tradeDate <= :end_date'
            params['end_date'] = pd.to_datetime(start_date).strftime("%Y-%m-%d")

        docs = col.find(query)\
            .bind(params)\
            .execute()

        dailyDatas = docs.fetch_all()

        variables = dailyDatas[0].keys()
        names = []
        for v in variables:
            names.append(convert_to_underline(v))
        print(names)
        df = pd.DataFrame([[getattr(i, j) for j in variables] for i in dailyDatas], columns=names)
        df = df[['trade_date','ts_code','low','vol','high','open','pre_close','close','amount','pct_chg']]
        df['trade_date'] = df.trade_date.str[:10]

        df.index = pd.to_datetime(df.trade_date)
        df = df.sort_index()
        session.close()
        return df
