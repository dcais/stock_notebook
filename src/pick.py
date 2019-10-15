import sys
import concurrent.futures
from os.path import abspath, join, dirname
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
sys.path.insert(0, join(abspath(dirname(__file__)), '..'))

from src.stock import Stock
from src.strategy import FirstStrategy


def get_blank_df():
    return pd.DataFrame(
        columns=['symbol', 'balance', 'balance_max', 'balance_min', 'profit', 'profit_max', 'profit_min'])


def simulate(symbol):
    logging.info("start simulate " + symbol)
    stragety = FirstStrategy(stock, symbol, start_date="2012-01-01")
    df = stragety.simulate(start_date="20180101",
                           init_amount=init_amount,
                           max_add_count=max_add_cnt,
                           stop_price_factor=stop_price_factor
                           )

    rdf = None
    if df is not None:
        return df.tail(1)
    else:
        pass

    return rdf


def simu_callback(future):
    pass


if __name__ == '__main__':
    stock = Stock()
    init_amount = 100000
    worker_cnt = 2
    max_add_cnt = 4
    stop_price_factor = 4
    if len(sys.argv) >= 2:
        worker_cnt = int(sys.argv[1])
    if len(sys.argv) >= 3:
        max_add_cnt = int(sys.argv[2])
    if len(sys.argv) >= 4:
        stop_price_factor = int(sys.argv[2])
    print("worker count = %s, max add count %s, stop_price_factor %s" % (worker_cnt, max_add_cnt, stop_price_factor))
    df_concept_detail = stock.get_concept_detail()
    df = None
    with concurrent.futures.ProcessPoolExecutor(max_workers=worker_cnt) as executor:
        ft_map = {executor.submit(simulate, row['symbol']): row['symbol'] for i, row in stock.stock_df.iterrows()}
        for future in concurrent.futures.as_completed(ft_map):
            symbol = ft_map[future]
            try:
                df_i = future.result()
                if df_i is not None:
                    ts_code = df_i['ts_code'][0]

                    if ts_code in df_concept_detail.index:
                        concept_details = df_concept_detail.loc[ts_code:ts_code]
                        df_i['concepts'] = ",".join(concept_details['concept_name'].to_numpy().tolist())
                    else:
                        df_i['concepts'] = ''

                    logging.info("simulate %s finished " % symbol)
                    if df is None:
                        df = df_i
                    else:
                        df = df.append(df_i)
                else:
                    logging.info("simulate %s finished, the result is None", symbol)

            except Exception as exc:
                logging.error('%s generated an exception: %s' % (symbol, exc))
            else:
                pass

    df.index = df['ts_code']

    df_hs300 = stock.get_hs_300()
    df_hs300['hs300'] = 'Y'
    df_hs300 = df_hs300[['hs300']]
    df = pd.merge(df, df_hs300, left_index=True, right_index=True, how='left')

    df_zz500 = stock.get_zz_500()
    df_zz500['zz500'] = 'Y'
    df_zz500 = df_zz500[['zz500']]
    df = pd.merge(df, df_zz500, left_index=True, right_index=True, how='left')

    df_sz50 = stock.get_sz_50()
    df_sz50['sz50'] = 'Y'
    df_sz50 = df_sz50[['sz50']]
    df = pd.merge(df, df_sz50, left_index=True, right_index=True, how='left')

    df.to_excel("pick.xlsx")
