import sys
import concurrent.futures
from os.path import abspath, join, dirname
import pandas as pd

sys.path.insert(0, join(abspath(dirname(__file__)), '..'))
dirpath = join(abspath(dirname(__file__)), '..')
outpath = join(dirpath, 'out')

from src.simulate import simulate
from src.stock import Stock
from src.strategy import FirstStrategy
import pandas as pd
from .log import init_log

logging = init_log()

stock = Stock()


def simulate_one(param):
    data_start_date = param['data_start_date']
    simulate_start_date = param['simulate_start_date']
    simulate_end_date = param['simulate_end_date']
    strategy_name = param['strategy_name']
    strategy_ctx = param['strategy_ctx']
    ts_code = param['ts_code']

    result = simulate(ts_code, stock,
                      data_start_date=data_start_date,
                      simulate_start_date=simulate_start_date,
                      simulate_end_date=simulate_end_date,
                      strategy_name=strategy_name,
                      strategy_ctx=strategy_ctx,
                      )
    account = result['account'].tail(1)
    last_day_data = result['daily_data'].tail(1)
    last_position = result['position'].tail(1)
    account_report = result['account_report']
    account = pd.concat([account, account_report], axis=1)
    account['ts_code'] = ts_code
    last_day_data['ts_code'] = ts_code
    last_position['ts_code'] = ts_code
    account = account.loc[:, ~account.columns.duplicated()]
    return {
        'account':account,
        'daily_data':last_day_data,
        'position': last_position
    }


def run_simulate(
        worker_cnt=2,
        stock=None,
        stock_pool=None,
        strategy_name="turtle55",
        data_start_date='20020101',
        simulate_start_date='20090101',
        simulate_end_date='',
        strategy_ctx={},
        excel_path=''

):
    df_account: pd.DataFrame = None
    df_daily: pd.DataFrame = None
    df_position: pd.DataFrame = None
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
                dic_result = future.result()
                if dic_result is None:
                    logging.info("simulate %s %s finished, the result is None", ts_code, strategy_name)
                else:
                    df_i_account = dic_result['account']
                    df_i_daily = dic_result['daily_data']
                    df_i_position = dic_result['position']
                    if df_account is None:
                        df_account = df_i_account.copy()
                    else:
                        logging.info("simulate %s %s finished, profit %f" % (ts_code, strategy_name, df_i_account.profit_rate[0]))
                        df_account = df_account.append(df_i_account,ignore_index=True)

                    if df_daily is None:
                        df_daily = df_i_daily.copy()
                    else:
                        df_daily = df_daily.append(df_i_daily, ignore_index=True)

                    if df_position is None:
                        df_position = df_i_position.copy()
                    else:
                        df_position = df_position.append(df_i_position,ignore_index=True)

            except Exception as exc:
                logging.error('%s %s generated an exception: %s' % (ts_code,strategy_name, exc))
            else:
                pass
    fall_rate_max = df_account.fall_rate.min()

    profit_rate_max = df_account.profit_rate.max()
    profit_rate_mean = df_account.profit_rate.mean()
    profit_rate_std = df_account.profit_rate.std()

    year_log_return_rate_max = df_account.year_log_return_rate.max()
    year_log_return_rate_mean = df_account.year_log_return_rate.mean()
    year_log_return_rate_std = df_account.year_log_return_rate.std()

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

    path = excel_path
    writer = pd.ExcelWriter(path=path)
    df_account.to_excel(writer, sheet_name='detail')
    df_daily.to_excel(writer, sheet_name='last_day')
    df_report.to_excel(writer, sheet_name='report')
    df_position.to_excel(writer, sheet_name='position')
    writer.save()


def run_simulate_pool(
        strategy_pool:list,
        stock_pool:list,
        data_start_date:str,
        simulate_start_date:str,
        simulate_end_date:str,
        excel_path_pre:str,
        worker_cnt: int = 2,
):
    for stratege in strategy_pool:
        strategy_name = stratege['name']
        strategy_ctx = stratege['ctx']
        excel_name = stratege['excel_name'] if 'excel_name' in stratege else strategy_name
        run_simulate(
            worker_cnt=worker_cnt,
            stock=stock,
            stock_pool=stock_pool,
            strategy_name=strategy_name,
            strategy_ctx= strategy_ctx,
            data_start_date=data_start_date,
            simulate_start_date=simulate_start_date,
            simulate_end_date = simulate_end_date,
            excel_path=excel_path_pre + '_' + excel_name + '.xlsx'
        )
