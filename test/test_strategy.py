import sys
from os.path import abspath, join, dirname
import pandas as pd
sys.path.insert(0, join(abspath(dirname(__file__)), '..'))

from src.stock import Stock
from src.strategy import FirstStrategy

stock = Stock()
init_amount = 100000

ret_df = pd.DataFrame(columns=['symbol','balance','balance_max','balance_min','profit','profit_max','profit_min'])

for i, row in stock.stock_df.iterrows():
    symbol = row['symbol'];
    print ("start simulate "+ row['symbol'])
    stragety = FirstStrategy(stock, symbol, start_date="2012-01-01")
    df = stragety.simulate(start_date="20180101",
                           init_amount=init_amount)
    balance = df.tail(1)['balance'][0]
    balance_max = df.max()['balance']
    balance_min = df.min()['balance']
    profit = (balance - init_amount) / init_amount
    profit_max = (balance_max - init_amount) / init_amount
    profit_min = (balance_min - init_amount) / init_amount
    ret_df = ret_df.append(
        {'symbol': symbol,
         'balance': balance,
         'balance_max': balance_max,
         'balance_min': balance_min,
         'profit': profit,
         'profit_max': profit_max,
         'profit_min': profit_min
         }, ignore_index=True)

ret_df.to_excel("summary.xlsx");
