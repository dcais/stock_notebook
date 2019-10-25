import src.log as log
import numpy as np
from .strategy_turtle_55 import StrategyTurtle55
from .position_mgr_turtle import PositionMgrTurtle
from .position_mgr_adosc import PositionMgrAdosc
from .chart import Chart
from .strategy_adosc import StrategyAdosc
from .strategy_turtle_20 import StrategyTurtle20
from pyecharts import options as opts
from .strategy_ma_2 import StrategyMa2
from .strategy_ma_3 import StrategyMa3
from .position_mgr_ma import PositionMgrMa
from .position_mgr_turtle_trace_stop import PositionMgrTurtleTraceStop


def get_k_chart(
        stock_info,
        strategy_name,
        df_daily,
        df_position,
        df_trade_detail,
        strategy_ctx:dict = {}
):
    chart = Chart()
    kdatas = np.array(df_daily.loc[:, ['open', 'close', 'low', 'high']])
    vols = np.array(df_daily['vol'])
    trade_dates = df_daily.trade_date.to_numpy()
    ma_dic = {}
    ma_periods = []

    tanqian_dic = None
    if strategy_name == 'turtle55' or strategy_name == 'turtle20' or strategy_name == 'turtle55_trace_stop':
        ma_periods = [25, 350]
        tanqian_dic = {
            'max_l': {
                'name': 'L_MAX',
                'datas': df_daily['max_l'].to_numpy().round(2).tolist()
            },
            'min_s': {
                'name': 'S_MIN',
                'datas': df_daily['min_s'].to_numpy().round(2).tolist()
            }
        }

    elif strategy_name == 'adosc':
        ma_periods = [8, 17, 25, 99, 145, 318]
    elif strategy_name == 'ma2':
        period = strategy_ctx['short_period']
        ma_dic['MA'+str(period)] = {
            'name': 'MA'+str(period),
            'datas': df_daily['ma_s'].to_numpy().round(2).tolist()
        }
        period = strategy_ctx['long_period']
        ma_dic['MA' + str(period)] = {
            'name': 'MA' + str(period),
            'datas': df_daily['ma_l'].to_numpy().round(2).tolist()
        }
    elif strategy_name == 'ma3':
        period = strategy_ctx['short_period']
        ma_dic['MA'+str(period)] = {
            'name': 'MA'+str(period),
            'datas': df_daily['ma_s'].to_numpy().round(2).tolist()
        }
        period = strategy_ctx['mid_period']
        ma_dic['MA' + str(period)] = {
            'name': 'MA' + str(period),
            'datas': df_daily['ma_m'].to_numpy().round(2).tolist()
        }
        period = strategy_ctx['long_period']
        ma_dic['MA' + str(period)] = {
            'name': 'MA' + str(period),
            'datas': df_daily['ma_l'].to_numpy().round(2).tolist()
        }

    for period in ma_periods:
        name = 'MA' + str(period)
        ma_dic[name] = {}
        ma_dic[name]['name'] = name
        ma_dic[name]['datas'] = df_daily[name].to_numpy().round(2).tolist()


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

    chart_sub_1 = chart.get_empty()
    if strategy_name == 'adosc':
        chart_sub_1 = chart.get_adosc_chart(df_daily)

    chart_k.add(
        chart_sub_1,
        grid_opts=opts.GridOpts(
            pos_left="6%", pos_right="8%", pos_top="68%", height="7%"
        ),
    )
    chart_sub_2 = chart.get_empty()

    chart_k.add(
        chart_sub_2,
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
        strategy_ctx = {},
        excel_path=None,
        with_chart = False,
):
    stock_info = stock.get_stock_info(keyword)
    df = stock.get_daily_data(stock_info['code'], data_start_date)

    if strategy_name == 'turtle55':
        strategy = StrategyTurtle55(df, ctx=strategy_ctx)
        positionMgr = PositionMgrTurtle()
    elif strategy_name == 'turtle55_trace_stop':
        strategy_ctx['use_stop_price'] = True
        strategy = StrategyTurtle55(df, ctx=strategy_ctx)
        positionMgr = PositionMgrTurtleTraceStop()
    elif strategy_name == 'turtle20':
        strategy = StrategyTurtle20(df, ctx=strategy_ctx)
        positionMgr = PositionMgrTurtle()
    elif strategy_name == 'adosc':
        strategy = StrategyAdosc(df, ctx=strategy_ctx)
        positionMgr = PositionMgrAdosc()
    elif strategy_name == 'ma2':
        strategy = StrategyMa2(df, ctx=strategy_ctx)
        positionMgr = PositionMgrMa()
    elif strategy_name == 'ma3':
        strategy = StrategyMa3(df, ctx=strategy_ctx)
        positionMgr = PositionMgrMa()

    result_dic = strategy.simulate(start_day=simulate_start_date, end_day=simulate_end_date, positionMgr=positionMgr,
                                   excel_path=excel_path)

    if with_chart:
        chart_k = get_k_chart(stock_info, strategy_name, result_dic['daily_data'], result_dic['position'],
                              result_dic['trade_detail'], strategy_ctx=strategy_ctx)
        chart_account = get_account_chart(stock_info, result_dic['account'])
        result_dic['chart'] = {
            'k': chart_k,
            'account': chart_account
        }

    return result_dic
