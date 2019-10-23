import pandas as pd
import talib as talib
import numpy as np
# import sys
# from os.path import abspath, join, dirname
# sys.path.insert(0, join(abspath(dirname(__file__)), '..'))
from .strategy_base import StrategyBase
from .account import Account
from .position_mgr import PositionMgr


class StrategyAdosc(StrategyBase):

    def init_data(self, df: pd.DataFrame):
        df['ATR'] = talib.ATR(df.high, df.low, df.close, timeperiod=25)
        df['ADOSC'] = talib.ADOSC(df.high, df.low, df.close, df.vol, fastperiod=3, slowperiod=10)
        df['sar'] = talib.SAR(df.high, df.low, acceleration=0.1, maximum=2)
        df['ADOSC_trend'] = df['ADOSC'] - df['ADOSC'].shift(1)
        df['ADOSC_trend_5'] = df['ADOSC'] - df['ADOSC'].shift(5)
        df['signal'] = ''

        ma_periods = [8, 17, 25, 99, 145, 318]

        for period in ma_periods:
            name = "MA" + str(period)
            ma = talib.EMA(np.array(df.close), period)
            df[name] = ma

        df['MA17_trend'] = df['MA17'] - df['MA17'].shift(1)
        df['MA25_trend'] = df['MA25'] - df['MA25'].shift(1)
        df['MA17_trend_5'] = df['MA17'] - df['MA17'].shift(5)
        df['MA25_trend_5'] = df['MA25'] - df['MA25'].shift(5)

    def init_ctx(self, ctx: dict):
        account_risk = 0.01
        stop_price_factor = 2.5
        max_add_count = 4

        ctx['account_risk'] = 0.01
        ctx['stop_price_factor'] = 2.5
        ctx['max_add_count'] = 4

    def before_run(self, df: pd.DataFrame):
        cond1 = (df['close'] > df['sar']) & (df['close'] > df['MA8']) & (df['ADOSC'] > 0) & (df['ADOSC_trend_5'] > 0)
        df.loc[cond1, ['signal']] = 'pre_buy'

    def run_strategy(self, trade_day, df_day: pd.DataFrame, account: Account, positionMgr: PositionMgr,
                     ctx: dict = {}):
        len_df_day = len(df_day)
        series_today = df_day.tail(1).iloc[0]
        series_yes = df_day.iloc[len_df_day - 2]

        if series_yes['signal'] == 'pre_buy' and positionMgr.is_unit_empty():
            unit_price = series_today['open']
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

        if positionMgr.unit_account > 0 and positionMgr.position_day > 0 and series_today.low < stop_price:
            unit_price = min(stop_price, series_today.high)
            positionMgr.close(trade_date=trade_day, unit_price=unit_price, account=account)
