import sys
import concurrent.futures
from os.path import abspath, join, dirname
import pandas as pd

sys.path.insert(0, join(abspath(dirname(__file__)), '..'))

from src.stock import Stock
from src.strategy import FirstStrategy


def get_blank_df():
    return pd.DataFrame(
        columns=['symbol', 'balance', 'balance_max', 'balance_min', 'profit', 'profit_max', 'profit_min'])


def simulate(symbol):
    print("start simulate " + symbol)
    stragety = FirstStrategy(stock, symbol, start_date="2012-01-01")
    df = stragety.simulate(start_date="20180101",
                           init_amount=init_amount)

    rdf = None
    if df is not None:
        balance = df.tail(1)['balance'][0]
        balance_max = df.max()['balance']
        balance_min = df.min()['balance']
        profit = (balance - init_amount) / init_amount
        profit_max = (balance_max - init_amount) / init_amount
        profit_min = (balance_min - init_amount) / init_amount
        df = get_blank_df()
        rdf = df.append(
            {'symbol': symbol,
             'balance': balance,
             'balance_max': balance_max,
             'balance_min': balance_min,
             'profit': profit,
             'profit_max': profit_max,
             'profit_min': profit_min
             }, ignore_index=True)
        # print("simulate %s finished, profit %f" % (symbol, profit))
    else:
        pass

    return rdf


def simu_callback(future):
    pass


if __name__ == '__main__':
    stock = Stock()
    init_amount = 100000
    worker_cnt = 2;
    if len(sys.argv) >= 2:
        worker_cnt = int(sys.argv[1])

    print("worker count = %s" % worker_cnt)
    df = get_blank_df()
    with concurrent.futures.ProcessPoolExecutor(max_workers=worker_cnt) as executor:
        ft_map = {executor.submit(simulate, row['symbol']): row['symbol'] for i, row in stock.stock_df.iterrows()}
        for future in concurrent.futures.as_completed(ft_map):
            symbol = ft_map[future]
            try:
                df_i = future.result()
                if df_i is not None:
                    print("simulate %s finished, profit %f" % (symbol, df_i['profit'][0]))
                    df = df.append(df_i)
                else:
                    print("simulate %s finished, the result is None",symbol)

            except Exception as exc:
                print(' generated an exception: %s' % exc)
            else:
                pass

    df.to_excel("summary.xlsx");
