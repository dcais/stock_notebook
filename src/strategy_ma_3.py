import pandas as pd
import talib as talib
import numpy as np
# import sys
# from os.path import abspath, join, dirname
# sys.path.insert(0, join(abspath(dirname(__file__)), '..'))
from .strategy_base import StrategyBase
from .account import Account
from .position_mgr import PositionMgr
from .utils.calc import HMA


class StrategyMa3(StrategyBase):
    last_win_ignored = True

    def init_data(self, df: pd.DataFrame):
        df['ATR'] = talib.ATR(df.high, df.low, df.close, timeperiod=20)
        df['signal'] = ''

        lp = self.ctx['long_period']
        mp = self.ctx['mid_period']
        sp = self.ctx['short_period']

        ma_type = 'EMA'
        if 'ma_type' in self.ctx:
            ma_type = self.ctx['ma_type']

        if ma_type == 'EMA':
            df['ma_l'] = talib.EMA(np.array(df.close), lp)
            df['ma_m'] = talib.EMA(np.array(df.close), mp)
            df['ma_s'] = talib.EMA(np.array(df.close), sp)
        elif ma_type == 'WMA':
            df['ma_l'] = talib.WMA(np.array(df.close), lp)
            df['ma_m'] = talib.WMA(np.array(df.close), mp)
            df['ma_s'] = talib.WMA(np.array(df.close), sp)
        elif ma_type == 'HMA':
            df['ma_l'] = HMA(np.array(df.close), lp)
            df['ma_m'] = HMA(np.array(df.close), mp)
            df['ma_s'] = HMA(np.array(df.close), sp)


    def init_ctx(self, ctx: dict):
        pass

    def before_run(self, df: pd.DataFrame):
        cond_signal_open_1 = (df.ma_s > df.ma_m) & (df.ma_s.shift(1) < df.ma_m.shift(1)) & (df.ma_s > df.ma_l) & (
                df.ma_m > df.ma_l)

        cond_signal_open_2 = (df.ma_m > df.ma_l) & (df.ma_m.shift(1) < df.ma_l.shift(1)) & (df.ma_s > df.ma_m)

        df.loc[cond_signal_open_1 | cond_signal_open_2, ['signal']] = 'open'

        cond_signal_close_1 = (df.ma_s < df.ma_m) & (df.ma_s.shift(1) > df.ma_m.shift(1))
        cond_signal_close_2 = (df.ma_s < df.ma_l) & (df.ma_s.shift(1) > df.ma_l.shift(1))
        cond_signal_close_3 = (df.ma_m < df.ma_l) & (df.ma_m.shift(1) > df.ma_l.shift(1))
        df.loc[cond_signal_close_1 | cond_signal_close_2 | cond_signal_close_3, ['signal']] = 'close'
        pass

    def run_strategy(self, trade_day, df_day: pd.DataFrame, account: Account, positionMgr: PositionMgr,
                     ctx: dict = {}):
        len_df_day = len(df_day)
        series_today = df_day.tail(1).iloc[0]
        series_yes = df_day.iloc[len_df_day - 2]

        add_prices = []
        if positionMgr.is_unit_empty() and series_today.signal == 'open':
            unit_price = series_today.high
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

        # stop_price = positionMgr.stop_price
        #
        if positionMgr.unit_account > 0 and series_today.signal == 'close':
            unit_price = series_today.close
            positionMgr.close(trade_date=trade_day, unit_price=unit_price, account=account)
        #
        # if positionMgr.unit_account > 0 and positionMgr.position_day > 0 and series_today.low < series_today.min_s:
        #     unit_price = min(series_today.min_s, series_today.high)
        #     positionMgr.close(trade_date=trade_day, unit_price=unit_price, account=account)
