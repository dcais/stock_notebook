import pandas as pd
import talib as talib
import numpy as np
# import sys
# from os.path import abspath, join, dirname
# sys.path.insert(0, join(abspath(dirname(__file__)), '..'))
from .strategy_base import StrategyBase
from .account import Account
from .position_mgr import PositionMgr


class StrategyTurtle55(StrategyBase):

    def init_data(self, df: pd.DataFrame):
        df['ATR'] = talib.ATR(df.high, df.low, df.close, timeperiod=20)
        df['signal'] = ''

        df['max_55'] = talib.MAX(df.high, timeperiod=55).shift(1)
        # 最近N2个交易日最低价
        df['min_20'] = talib.MIN(df.low, timeperiod=20).shift(1)

        ma_periods = [25, 350]

        for period in ma_periods:
            name = "MA" + str(period)
            ma = talib.EMA(np.array(df.close), period)
            df[name] = ma

    def init_ctx(self, ctx: dict):
        pass

    def before_run(self, df: pd.DataFrame):
        cond_signal_open = df.high > df.max_55
        df.loc[cond_signal_open , ['signal']] = 'open'

        cond_signal_close = df.low < df.min_20
        df.loc[cond_signal_close , ['signal']] = 'close'
        pass

    def run_strategy(self, trade_day, df_day: pd.DataFrame, account: Account, positionMgr: PositionMgr,
                     ctx: dict = {}):
        len_df_day = len(df_day)
        series_today = df_day.tail(1).iloc[0]
        series_yes = df_day.iloc[len_df_day - 2]

        if positionMgr.is_unit_empty() and series_today.signal == 'open':
            unit_price = max( series_today.max_55, series_today.low)
            positionMgr.buy(trade_date=trade_day, unit_price=unit_price, atr=series_yes.ATR, account=account)

        add_prices = positionMgr.add_prices
        if not positionMgr.is_unit_empty() and len(add_prices) > 0:
            for add_price in add_prices:
                pre_close = series_yes.close
                open_price = series_today.open
                low = series_today.low
                high = series_today.high
                unit_price = 0

                if add_price > pre_close and add_price < open_price:
                    unit_price = open_price

                elif add_price > low and add_price < high:
                    unit_price = add_price

                if unit_price > 0:
                    positionMgr.buy(trade_date=trade_day, unit_price=unit_price, atr=series_yes.ATR, account=account)
                    positionMgr.remove_add_price()

        stop_price = positionMgr.stop_price

        # if positionMgr.unit_account > 0 and positionMgr.position_day > 0 and series_today.low < stop_price:
        #     unit_price = min(stop_price, series_today.high)
        #     positionMgr.close(trade_date=trade_day, unit_price=unit_price, account=account)

        if positionMgr.unit_account > 0 and positionMgr.position_day > 0 and series_today.low < series_today.min_20:
            unit_price = min(series_today.min_20, series_today.high)
            positionMgr.close(trade_date=trade_day, unit_price=unit_price, account=account)
