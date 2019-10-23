import sys
import asyncio
from os.path import abspath, join, dirname
import pandas as pd
sys.path.insert(0, join(abspath(dirname(__file__)), '..'))

from src.ts_stock import TsStock
from src.strategy_base import StrategyBase


stock = TsStock()

df = stock.get_daily_data('002019','20170101')

strategy = StrategyBase(df)

strategy.simulate(start_day='20180101')