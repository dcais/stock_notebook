import sys
import asyncio
from os.path import abspath, join, dirname
import pandas as pd

sys.path.insert(0, join(abspath(dirname(__file__)), '..'))

import numpy as np
from src.ts_stock import TsStock
from src.strategy_turtle_55 import StrategyTurtle55
from src.position_mgr_turtle import PositionMgrTurtle
from src.chart import  Chart
from pyecharts import options as opts
# import

stock = TsStock()

symbol = '002032'
stock_info = stock.get_stock_info(symbol)

df = stock.get_daily_data(symbol, '20160101')

strategy = StrategyTurtle55(df)

positionMgr = PositionMgrTurtle()

result_dic = strategy.simulate(start_day='20180101', positionMgr=positionMgr, excel_path='test_strategy_turtle_' + symbol + '.xlsx');

chart = Chart()


daily_df = result_dic['daily_data']
kdatas = np.array(daily_df.loc[:,['open','close','low','high']])
vols = np.array(daily_df['vol'])
trade_dates = daily_df.trade_date.to_numpy()

ma_periods = [25, 350]

ma_dic = {}
for period in ma_periods:
    name = 'MA'+ str(period)
    ma_dic[name] = {}
    ma_dic[name]['name'] = name
    ma_dic[name]['datas'] = daily_df[name].to_numpy().round(2).tolist()

tanqian_dic = {
    'BUY_55_MAX': {
        'name': 'BUY_55_MAX',
        'datas': daily_df['max_55'].to_numpy().round(2).tolist()
    },
    'BUY_20_MIN': {
        'name': 'BUY_20_MIN',
        'datas': daily_df['min_20'].to_numpy().round(2).tolist()
    }
}
bs = {
}

df_trade_detail = result_dic['trade_detail']
df_position = result_dic['position']

bs['buy'] = df_trade_detail.loc[df_trade_detail['trade_type'] == 'buy',['trade_date','unit_price']]
bs['sell'] = df_trade_detail.loc[df_trade_detail['trade_type'] == 'sell', ['trade_date','unit_price']]

df_stop_price = df_position.loc[df_position['unit_account']>0,['trade_date','stop_price']]

chart_k = chart.get_grid(
    stock_info,
    trade_dates.tolist(),
    kdatas.tolist(),
    vols.tolist(),
    ma_dic= ma_dic,
    tanqian_dic = tanqian_dic,
    bs = bs,
    df_stop_price = df_stop_price
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

df_account = result_dic['account']
chart_account = chart.get_line_account(df_account,stock_info)



chart_k.render("test_strategy.html")
chart_account.render("test_account.html")

