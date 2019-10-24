import sys
import concurrent.futures
from os.path import abspath, join, dirname
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S %p')
sys.path.insert(0, join(abspath(dirname(__file__)), '..'))
dirpath = join(abspath(dirname(__file__)), '..')
outpath = join(dirpath, 'out')

from src.simulate import simulate
from src.stock import Stock
from src.strategy import FirstStrategy
import pandas as pd


def get_stock_pool():
    # return ['000001.SZ','002019.SZ']
    return stock.get_hs_300().ts_code.to_numpy().tolist()


stock = Stock()


def simulate_one(param):
    data_start_date = param['data_start_date']
    simulate_start_date = param['simulate_start_date']
    simulate_end_date = param['simulate_end_date']
    strategy_name = param['strategy_name']
    strategy_ctx = param['strategy_ctx']

    result = simulate(param['ts_code'], stock,
                      data_start_date=data_start_date,
                      simulate_start_date=simulate_start_date,
                      simulate_end_date=simulate_end_date,
                      strategy_name=strategy_name,
                      strategy_ctx=strategy_ctx,
                      )
    account = result['account'].tail(1)
    account_report = result['account_report']
    account = pd.concat([account, account_report], axis=1)
    account['ts_code'] = param['ts_code']
    account = account.loc[:, ~account.columns.duplicated()]
    return account


def run_simulate(
        worker_cnt=2,
        stock=None,
        stock_pool=None,
        strategy_name="turtle55",
        data_start_date='20020101',
        simulate_start_date='20090101',
        simulate_end_date='',
        strategy_ctx={},
        excel_path_pre=''

):
    df: pd.DataFrame = None
    print("worker count = %s" % worker_cnt)
    with concurrent.futures.ProcessPoolExecutor(max_workers=worker_cnt) as executor:
        arr1 = ['hello', 'world']
        ft_map = {}
        for ts_code in stock_pool:
            r = executor.submit(simulate_one, {
                'ts_code': ts_code,
                'data_start_date': data_start_date,
                'simulate_start_date': simulate_start_date,
                'simulate_end_date': simulate_end_date,
                'strategy_name': strategy_name,
                'strategy_ctx': strategy_ctx
            })
            ft_map[r] = ts_code

        for future in concurrent.futures.as_completed(ft_map):
            ts_code = ft_map[future]
            try:
                df_i = future.result()
                if df is None:
                    df = df_i.copy()
                else:
                    if df_i is not None:
                        logging.info("simulate %s %s finished, profit %f" % (ts_code, strategy_name, df_i.profit_rate[0]))
                        df = df.append(df_i)
                    else:
                        logging.info("simulate %s %s finished, the result is None", ts_code,strategy_name)

            except Exception as exc:
                logging.error('%s %s generated an exception: %s' % (ts_code,strategy_name, exc))
            else:
                pass
    fall_rate_max = df.fall_rate.min()

    profit_rate_max = df.profit_rate.max()
    profit_rate_mean = df.profit_rate.mean()
    profit_rate_std = df.profit_rate.std()

    year_log_return_rate_max = df.year_log_return_rate.max()
    year_log_return_rate_mean = df.year_log_return_rate.mean()
    year_log_return_rate_std = df.year_log_return_rate.std()

    df_report = pd.DataFrame([
        (
            fall_rate_max,
            profit_rate_max,
            profit_rate_mean,
            profit_rate_std,
            year_log_return_rate_max,
            year_log_return_rate_mean,
            year_log_return_rate_std
        )
    ],
        columns=[
            'fall_rate_max',
            'profit_rate_max',
            'profit_rate_mean',
            'profit_rate_std',
            'year_log_return_rate_max',
            'year_log_return_rate_mean',
            'year_log_return_rate_std'
        ])

    path = excel_path_pre + "_" + strategy_name + '.xlsx'
    writer = pd.ExcelWriter(path=path)
    df.to_excel(writer, sheet_name='detail')
    df_report.to_excel(writer, sheet_name='report')
    writer.save()


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
    data_start_date = '20070101'
    simulate_start_date = '20080101'

    for stratege in strategy_pool:
        run_simulate(
            worker_cnt=worker_cnt,
            stock=stock,
            stock_pool=stock_pool,
            strategy_name=stratege['name'],
            strategy_ctx=stratege['ctx'],
            data_start_date=data_start_date,
            simulate_start_date=simulate_start_date,
            excel_path_pre=join(outpath, 'test_simulate_hs300')
        )
