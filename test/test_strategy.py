import sys
from os.path import abspath, join, dirname
import pandas as pd
sys.path.insert(0, join(abspath(dirname(__file__)), '../src'))

from stock import Stock
from strategy import FirstStrategy

stock = Stock()
init_amount = 100000

global g_ret_df
g_ret_df = pd.DataFrame(columns=['symbol','balance','balance_max','balance_min','profit','profit_max','profit_min'])

def simulate(symbol,ret_df):
    print ("start simulate "+ symbol)
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
        rdf = ret_df.append(
            {'symbol': symbol,
             'balance': balance,
             'balance_max': balance_max,
             'balance_min': balance_min,
             'profit': profit,
             'profit_max': profit_max,
             'profit_min': profit_min
             }, ignore_index=True)
        print ("simulate "+ row['symbol']+"finished, profit"+str(profit))
    else:
        print ("simulate "+ row['symbol']+"finished, the result is None")

    return rdf

for i, row in stock.stock_df.iterrows():
    symbol = row['symbol']
    try:
        df = simulate(symbol,g_ret_df)
        if df is not None:
            g_ret_df = df;
        print(g_ret_df)
    except:
        print ("Error: "+symbol+"fail")
    else:
        pass


g_ret_df.to_excel("summary.xlsx");
