import sys
from os.path import abspath, join, dirname

sys.path.insert(0, join(abspath(dirname(__file__)), '..'))
dirpath = join(abspath(dirname(__file__)), '..')
outpath = join(dirpath, 'out')

from src.stock import Stock
from src.simulate_pool import run_simulate_pool
from src.test_strategy_pool import get_strategy_pool

from src.log import  init_log
logging = init_log()

stock = Stock()

def get_stock_pool():
    return [
        '600000.SH',
        '002032.SZ',
        '600030.SH',
        '601318.SH',
        '000001.SZ',
        '000002.SZ',
        '600612.SH',
        '600188.SH',
        '600340.SH',
        '600048.SH',
        '000048.SH',
        '601966.SH',
        '002821.SH',
        '603129.SH',
        '000661.SH',
        '600132.SH',
        '300690.SZ',
        '300122.SZ',
        '002841.SZ',
        '600720.SH',
        '300498.SZ',
        '603360.SH',
        '688388.SH',
        '300487.SZ',
        '002714.SZ',
        '603160.SZ',
        '300702.SZ',
        '002234.SZ',
        '600876.SH',
    ]

if __name__ == '__main__':
    init_amount = 100000
    worker_cnt = 2
    max_add_cnt = 4
    stop_price_factor = 4
    if len(sys.argv) >= 2:
        worker_cnt = int(sys.argv[1])

    stock_pool = get_stock_pool()
    strategy_pool = get_strategy_pool()

    data_start_date = '20040101'
    simulate_start_date = '20080101'

    run_simulate_pool(
        strategy_pool=strategy_pool,
        stock_pool=stock_pool,
        data_start_date=data_start_date,
        simulate_start_date=simulate_start_date,
        simulate_end_date= '',
        excel_path_pre = join(outpath, 'test_simulate_mine'),
        worker_cnt = worker_cnt
    )
