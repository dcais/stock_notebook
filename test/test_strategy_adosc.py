import sys
import asyncio
from os.path import abspath, join, dirname
import pandas as pd

sys.path.insert(0, join(abspath(dirname(__file__)), '..'))

from src.ts_stock import TsStock
from src.strategy_adosc import StrategyAdosc
from src.position_mgr import PositionMgr

# import

stock = TsStock()

symbol = '002019'

df = stock.get_daily_data(symbol, '20080101')

strategy = StrategyAdosc(df)

positionMgr = PositionMgr(account_risk=0.01, stop_atr_factor=4, max_buy_cnt=4)

strategy.simulate(start_day='20090101', positionMgr=positionMgr, excel_path='test_strategy_adsoc_' + symbol + '.xlsx');
