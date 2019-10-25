import logging
import sys
from os.path import abspath, join, dirname

logging.basicConfig(level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S %p')
sys.path.insert(0, join(abspath(dirname(__file__)), '..'))
dirpath = join(abspath(dirname(__file__)), '..')
outpath = join(dirpath, 'out')

from src.stock import Stock
from src.simulate_pool import run_simulate_pool

stock = Stock()

def get_stock_pool():
    # return ['000001.SZ','002019.SZ']
    return stock.get_hs_300().ts_code.to_numpy().tolist()

def get_strategy_pool():
    pool = []
    pool.append({
        'name': 'turtle55',
        'ctx': {
            'long_period': 55,
            'short_period': 20,
        }
    })
    pool.append({
        'name': 'turtle55',
        'ctx': {
            'long_period': 55,
            'short_period': 20,
            'max_hold_day': 80,
        },
        'excel_name':'turtle_55_hold_80'
    })
    pool.append({
        'name': "turtle20",
        'ctx': {
            'long_period': 20,
            'short_period': 10,
        }
    })
    pool.append({
        'name': "adosc",
        'ctx': {
        }
    })

    pool.append({
        'name': "ma2",
        'ma_type': 'EMA',
        'ctx': {
            'short_period': 100,
            'long_period': 350,
        },
        'excel_name': 'ma2_ema_100_350'
    })

    pool.append({
        'name': "ma2",
        'ma_type': 'WMA',
        'ctx': {
            'short_period': 100,
            'long_period': 350,
        },
        'excel_name': 'ma2_wma_100_350'
    })

    pool.append({
        'name': "ma2",
        'ma_type': 'HMA',
        'ctx': {
            'short_period': 100,
            'long_period': 350,
        },
        'excel_name': 'ma2_hma_100_350'
    })

    pool.append({
        'name': "ma2",
        'ma_type': 'WMA',
        'ctx': {
            'short_period': 17,
            'long_period': 25,
        },
        'excel_name': 'ma2_wma_17_25'
    })

    pool.append({
        'name': "ma2",
        'ma_type': 'HMA',
        'ctx': {
            'short_period': 17,
            'long_period': 25,
        },
        'excel_name': 'ma2_hma_17_25'
    })

    pool.append({
        'name': "ma2",
        'ma_type': 'EMA',
        'ctx': {
            'short_period': 30,
            'long_period': 90,
        },
        'excel_name': 'ma2_ema_30_90'
    })

    pool.append({
        'name': "ma2",
        'ma_type': 'WMA',
        'ctx': {
            'short_period': 30,
            'long_period': 90,
        },
        'excel_name': 'ma2_wma_30_90'
    })

    pool.append({
        'name': "ma2",
        'ma_type': 'HMA',
        'ctx': {
            'short_period': 30,
            'long_period': 90,
        },
        'excel_name': 'ma2_hma_30_90'
    })

    pool.append({
        'name': "ma3",
        'ma_type': 'EMA',
        'ctx': {
            'short_period': 30,
            'mid_period': 60,
            'long_period': 90,
        },
        'excel_name': 'ma3_ema_30_60_90'
    })

    pool.append({
        'name': "ma3",
        'ma_type': 'WMA',
        'ctx': {
            'short_period': 30,
            'mid_period': 60,
            'long_period': 90,
        },
        'excel_name': 'ma3_wma_30_60_90'
    })

    pool.append({
        'name': "ma3",
        'ma_type': 'HMA',
        'ctx': {
            'short_period': 30,
            'mid_period': 60,
            'long_period': 90,
        },
        'excel_name': 'ma3_hma_30_60_90'
    })

    pool.append({
        'name': "ma3",
        'ma_type': 'EMA',
        'ctx': {
            'short_period': 43,
            'mid_period': 99,
            'long_period': 90,
        },
        'excel_name': 'ma3_ema_43_99_145'
    })

    pool.append({
        'name': "ma3",
        'ma_type': 'WMA',
        'ctx': {
            'short_period': 43,
            'mid_period': 99,
            'long_period': 145,
        },
        'excel_name': 'ma3_wma_43_99_145'
    })

    pool.append({
        'name': "ma3",
        'ma_type': 'HMA',
        'ctx': {
            'short_period': 43,
            'mid_period': 99,
            'long_period': 145,
        },
        'excel_name': 'ma3_hma_43_99_145'
    })

    pool.append({
        'name': "ma3",
        'ma_type': 'EMA',
        'ctx': {
            'short_period': 150,
            'mid_period': 250,
            'long_period': 350,
        },
        'excel_name': 'ma3_ema_150_250_350'
    })

    pool.append({
        'name': "ma3",
        'ma_type': 'WMA',
        'ctx': {
            'short_period': 150,
            'mid_period': 250,
            'long_period': 350,
        },
        'excel_name': 'ma3_wma_150_250_350'
    })

    pool.append({
        'name': "ma3",
        'ma_type': 'HMA',
        'ctx': {
            'short_period': 150,
            'mid_period': 250,
            'long_period': 350,
        },
        'excel_name': 'ma3_hma_150_250_350'
    })

    return pool


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
        excel_path_pre = join(outpath, 'test_simulate_hs300'),
        worker_cnt = worker_cnt
    )
