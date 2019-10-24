import src.log as log
import numpy as np
from .strategy_turtle_55 import StrategyTurtle55
from .position_mgr_turtle import PositionMgrTurtle
from .chart import Chart
from pyecharts import options as opts


def get_k_chart(stock_info, strategy_name, df_daily, df_position, df_trade_detail):
    chart = Chart()
    kdatas = np.array(df_daily.loc[:, ['open', 'close', 'low', 'high']])
    vols = np.array(df_daily['vol'])
    trade_dates = df_daily.trade_date.to_numpy()
    ma_dic = {}
    ma_periods = []
    if strategy_name == 'turtle55':
        ma_periods = [25, 350]
        pass

    tanqian_dic = None
    for period in ma_periods:
        name = 'MA' + str(period)
        ma_dic[name] = {}
        ma_dic[name]['name'] = name
        ma_dic[name]['datas'] = df_daily[name].to_numpy().round(2).tolist()
        tanqian_dic = {
            'BUY_55_MAX': {
                'name': 'BUY_55_MAX',
                'datas': df_daily['max_55'].to_numpy().round(2).tolist()
            },
            'BUY_20_MIN': {
                'name': 'BUY_20_MIN',
                'datas': df_daily['min_20'].to_numpy().round(2).tolist()
            }
        }

    bs = {
    }

    bs['buy'] = df_trade_detail.loc[df_trade_detail['trade_type'] == 'buy', ['trade_date', 'unit_price']]
    bs['sell'] = df_trade_detail.loc[df_trade_detail['trade_type'] == 'sell', ['trade_date', 'unit_price']]

    df_stop_price = df_position.loc[df_position['unit_account'] > 0, ['trade_date', 'stop_price']]

    chart_k = chart.get_grid(
        stock_info,
        trade_dates.tolist(),
        kdatas.tolist(),
        vols.tolist(),
        ma_dic=ma_dic,
        tanqian_dic=tanqian_dic,
        bs=bs,
        df_stop_price=df_stop_price
    )

    turnover_chart = chart.get_empty()

    chart_k.add(
        turnover_chart,
        grid_opts=opts.GridOpts(
            pos_left="6%", pos_right="8%", pos_top="68%", height="7%"
        ),
    )
    chart_k.add(
        turnover_chart,
        grid_opts=opts.GridOpts(
            pos_left="6%", pos_right="8%", pos_top="75%", height="7%"
        ),
    )
    return chart_k


def get_account_chart(stock_info, df_account):
    chart = Chart()
    chart_account = chart.get_line_account(df_account, stock_info)
    return chart_account


def simulate(
        keyword,
        stock,
        data_start_date:str,
        simulate_start_date:str,
        simulate_end_date='',
        strategy_name=None,
        excel_path=None,
        with_chart = False
):
    stock_info = stock.get_stock_info(keyword)
    df = stock.get_daily_data(stock_info['code'], data_start_date)

    if strategy_name == 'turtle55':
        strategy = StrategyTurtle55(df)
        positionMgr = PositionMgrTurtle()

    result_dic = strategy.simulate(start_day=simulate_start_date, end_day=simulate_end_date, positionMgr=positionMgr,
                                   excel_path=excel_path)

    if with_chart:
        chart_k = get_k_chart(stock_info, strategy_name, result_dic['daily_data'], result_dic['position'],
                              result_dic['trade_detail'])
        chart_account = get_account_chart(stock_info, result_dic['account'])
        result_dic['chart'] = {
            'k': chart_k,
            'account': chart_account
        }

    return result_dic
