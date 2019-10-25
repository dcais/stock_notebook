import logging
import sys
from os.path import abspath, join, dirname

logging.basicConfig(level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S %p')
sys.path.insert(0, join(abspath(dirname(__file__)), '..'))
dirpath = join(abspath(dirname(__file__)), '..')
outpath = join(dirpath, 'out')

from src.stock import Stock
from src.simulate_pool import run_simulate_pool
from src.test_strategy_pool import get_strategy_pool
from src.log import  init_log
init_log()

stock = Stock()

def get_stock_pool():
    # return ['000001.SZ','002019.SZ']
    return stock.get_sz_50().ts_code.to_numpy().tolist()

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
        excel_path_pre = join(outpath, 'test_simulate_hs300'),
        worker_cnt = worker_cnt
    )
