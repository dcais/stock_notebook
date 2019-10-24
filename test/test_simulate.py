import sys
import asyncio
from os.path import abspath, join, dirname
import pandas as pd

sys.path.insert(0, join(abspath(dirname(__file__)), '..'))

from src.simulate import simulate
from src.ts_stock import TsStock

stock = TsStock()
keyword = '002032'

result = simulate(keyword, stock,
         data_start_date='20020101',
         simulate_start_date='20090101',
         strategy_name='turtle55',
         excel_path='test_simulate' + keyword + '.xlsx',
         with_chart=True
         )

result['chart']['k'].render('test_simulate_k.html')
result['chart']['account'].render('test_simulate_account.html')
