import sys
import asyncio
from os.path import abspath, join, dirname
import pandas as pd
sys.path.insert(0, join(abspath(dirname(__file__)), '..'))

from src.stock import Stock
from src.strategy import FirstStrategy

stock = Stock()
init_amount = 100000

ret_df = pd.DataFrame(columns=['symbol','balance','balance_max','balance_min','profit','profit_max','profit_min'])

stragety = FirstStrategy(stock, '600609', start_date="2012-01-01")
df = stragety.simulate(start_date="20180101",
                           init_amount=init_amount)


df.to_excel("detail.xlsx");
