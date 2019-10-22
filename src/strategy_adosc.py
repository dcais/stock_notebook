import pandas as pd
import talib as talib
import numpy as np
import sys
from os.path import abspath, join, dirname

sys.path.insert(0, join(abspath(dirname(__file__)), '..'))
from src.strategy_base import StrategyBase


class StrategyAdsoc(StrategyBase):

    def init_data(self, df: pd.DataFrame):
        df['ATR'] = talib.ATR(df.high, df.low, df.close, timeperiod=20)
        df['ADOSC'] = talib.ADOSC(df.high, df.low, df.close, df.vol, fastperiod=3, slowperiod=10)

        df['sar'] = talib.SAR(df.high, df.low, acceleration=0.1, maximum=2)

        df['ADOSC_trend'] = df['ADOSC'] - df['ADOSC'].shift(1)
        df['ADOSC_trend_5'] = df['ADOSC'] - df['ADOSC'].shift(5)

        ma_periods = [8, 17, 25, 99, 145, 318]

        for period in ma_periods:
            name = "MA" + str(period)
            ma = talib.EMA(np.array(df.close), period)
            df[name] = ma

        pass

    def calc_signal_pre_buy(self, df:pd.DataFrame):
        cond1 = df['close'] > df['sar'] & df['close'] > df['MA8'] & df['ADOSC'] > 0 & df['ADSOC_trend_5'] > 0
        df.loc[cond1,['signal']] = 'pre_buy'

    def before_run(self, df: pd.DataFrame):
        self.calc_signal_pre_buy(df)
        pass