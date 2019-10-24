import sys
import asyncio
from os.path import abspath, join, dirname
import pandas as pd

sys.path.insert(0, join(abspath(dirname(__file__)), '..'))
dirpath = join(abspath(dirname(__file__)), '..')
outpath = join(dirpath, 'out')

from src.simulate import simulate
from src.ts_stock import TsStock

stock = TsStock()
keyword = '002019'

# strategy_ctx = {
#     'long_period': 55,
#     'short_period': 20,
# }
# strategy_name = 'turtle55'
#
# result = simulate(keyword, stock,
#                   data_start_date='20020101',
#                   simulate_start_date='20090101',
#                   strategy_name=strategy_name,
#                   strategy_ctx=strategy_ctx,
#                   excel_path=join(outpath, 'test_simulate_' + strategy_name + '_' + keyword + '.xlsx'),
#                   with_chart=True
#                   )
#
# result['chart']['k'].render(join(outpath, 'test_simulate_' + strategy_name + '_k.html'))
# result['chart']['account'].render(join(outpath, 'test_simulate_' + strategy_name + '_account.html'))
#
# strategy_name = 'adosc'
# result = simulate(keyword, stock,
#                   data_start_date='20020101',
#                   simulate_start_date='20090101',
#                   strategy_name=strategy_name,
#                   strategy_ctx=strategy_ctx,
#                   excel_path=join(outpath, 'test_simulate_' + strategy_name + '_' + keyword + '.xlsx'),
#                   with_chart=True
#                   )
#
# result['chart']['k'].render(join(outpath, 'test_simulate_' + strategy_name + '_k.html'))
# result['chart']['account'].render(join(outpath, 'test_simulate_' + strategy_name + '_account.html'))

strategy_ctx = {
    'long_period': 20,
    'short_period': 10,
}

strategy_name = 'turtle20'
result = simulate(keyword, stock,
                  data_start_date='20020101',
                  simulate_start_date='20090101',
                  strategy_name=strategy_name,
                  strategy_ctx=strategy_ctx,
                  excel_path=join(outpath, 'test_simulate_' + strategy_name + '_' + keyword + '.xlsx'),
                  with_chart=True
                  )

result['chart']['k'].render(join(outpath, 'test_simulate_' + strategy_name + '_k.html'))
result['chart']['account'].render(join(outpath, 'test_simulate_' + strategy_name + '_account.html'))