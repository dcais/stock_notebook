import sys
import concurrent.futures
from os.path import abspath, join, dirname
import pandas as pd
import logging
import re
import json
import mysqlx
logging.basicConfig(level=logging.INFO)
sys.path.insert(0, join(abspath(dirname(__file__)), '..'))

from src.stock import Stock

import tushare as ts
token='36d50a0386e9066b5c79c2de58ea2d3a9b980020041adc910f76bfc7'
ts.set_token(token)
pro=ts.pro_api()
connection_string = {
}

client_options = {
    'pooling': {
        "max_size": 10,
        "max_idle_time": 30000
    }
}

def get_blank_df():
    return pd.DataFrame(
        columns=['symbol', 'name', 'n_income', 'last_year_n_income', 'n_income_tobi', 'profit' ] )

def convert_to_underline(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def cal (stock_df):
    ts_code = stock_df.ts_code
    df_income = get_finance_income_df(ts_code)
    # df_income.to_excel("income.xlsx",sheet_name='Sheet_name_1')
    df_income.index = pd.to_datetime(df_income.ann_date)
    df_income = df_income.sort_index(ascending=True)

    df = df_income.drop_duplicates(["ann_date"], keep="last")[['n_income_attr_p']]
    df.rename(columns={'n_income_attr_p': 'n_income'}, inplace=True)
    df['last_year_n_income'] = df['n_income'].shift(4)
    df['tongbi_n_income'] = ( df['n_income'] - df['last_year_n_income'])/ df['last_year_n_income']
    return df.tail(1)

def get_finance_income_df(ts_code):

    config_path = join(abspath(dirname(__file__)), '../config.json')
    with open(config_path) as json_file:
        connection_string = json.load(json_file)

    x_client = mysqlx.get_client(connection_string, client_options)
    session = x_client.get_session()
    schema = session.get_schema('stock')
    col = schema.get_collection('stock_x_fin_income')
    query = "tsCode = :tscode"
    params = {
        "tscode": ts_code
    }

    docs = col.find(query) \
        .bind(params) \
        .execute()
    dailyDatas = docs.fetch_all()

    session.close()
    x_client.close()

    if len(dailyDatas) == 0:
        return None

    variables = dailyDatas[0].keys()
    names = []
    for v in variables:
        names.append(convert_to_underline(v))
    # print(names)
    df = pd.DataFrame([[getattr(i, j) for j in variables] for i in dailyDatas], columns=names)
    return df


if __name__ == '__main__':
    stock = Stock()
    init_amount = 100000
    worker_cnt = 2
    max_add_cnt = 4
    if len(sys.argv) >= 2:
        worker_cnt = int(sys.argv[1])
    print("worker count = %s, max add count %s" % (worker_cnt,max_add_cnt))
    df = get_blank_df()
    with concurrent.futures.ProcessPoolExecutor(max_workers=worker_cnt) as executor:
        ft_map = {executor.submit(cal, row): row['symbol'] for i, row in stock.stock_df.iterrows()}
        for future in concurrent.futures.as_completed(ft_map):
            symbol = ft_map[future]
            try:
                df_i = future.result()
                if df_i is not None:
                    df_i['symbol'] = symbol
                    logging.info("simulate %s finished, tongbi income growth %f" % (symbol, df_i['tongbi_n_income'][0]))
                    df = df.append(df_i)
                else:
                    logging.info("simulate %s finished, the result is None", symbol)

            except Exception as exc:
                logging.error('%s generated an exception: %s' % (symbol, exc))
            else:
                pass

    df.to_excel("finance_income.xlsx")
