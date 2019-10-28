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


def run(
        keyword,
        data_start_date: str,
        simulate_start_date: str,
        strategy_conf: dict = {},
        simulate_end_date: str = '',
):
    strategy_name = strategy_conf['name']
    strategy_ctx = strategy_conf['ctx']
    strategy_savename = strategy_conf['savename'] if 'savename' in strategy_conf  else strategy_name

    result = simulate(keyword, stock,
                      data_start_date=data_start_date,
                      simulate_start_date=simulate_start_date,
                      strategy_name=strategy_name,
                      strategy_ctx=strategy_ctx,
                      init_amount=1000000,
                      excel_path=join(outpath, 'test_simulate_' + strategy_savename + '_' + keyword + '.xlsx'),
                      with_chart=True
                      )
    result['chart']['k'].render(join(outpath, 'test_simulate_' + strategy_savename + '_k.html'))
    result['chart']['account'].render(join(outpath, 'test_simulate_' + strategy_savename + '_account.html'))


if __name__ == '__main__':
    keyword = '603444'
    strategy_ctx = {
        'short_period': 20,
        # 'mid_period': 60,
        'long_period': 55,
    }
    strategy_name = 'turtle55'
    data_start_date = '20150101'
    simulate_start_date = '20180101'
    strategy_conf = {
        'name': strategy_name,
        'ctx': strategy_ctx,

    }
    run(
        keyword=keyword,
        strategy_conf=strategy_conf,
        data_start_date=data_start_date,
        simulate_start_date=simulate_start_date
    )



# strategy_name = 'adosc'
# result = simulate(keyword, stock,
#                   data_start_date=data_start_date,
#                   simulate_start_date=simulate_start_date,
#                   strategy_name=strategy_name,
#                   strategy_ctx=strategy_ctx,
#                   excel_path=join(outpath, 'test_simulate_' + strategy_name + '_' + keyword + '.xlsx'),
#                   with_chart=True
#                   )
#
# result['chart']['k'].render(join(outpath, 'test_simulate_' + strategy_name + '_k.html'))
# result['chart']['account'].render(join(outpath, 'test_simulate_' + strategy_name + '_account.html'))
#
# strategy_ctx = {
#     'long_period': 20,
#     'short_period': 10,
# }
#
# strategy_name = 'turtle20'
# result = simulate(keyword, stock,
#                   data_start_date=data_start_date,
#                   simulate_start_date=simulate_start_date,
#                   strategy_name=strategy_name,
#                   strategy_ctx=strategy_ctx,
#                   excel_path=join(outpath, 'test_simulate_' + strategy_name + '_' + keyword + '.xlsx'),
#                   with_chart=True
#                   )
#
# result['chart']['k'].render(join(outpath, 'test_simulate_' + strategy_name + '_k.html'))
# result['chart']['account'].render(join(outpath, 'test_simulate_' + strategy_name + '_account.html'))
