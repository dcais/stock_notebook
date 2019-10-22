import pandas as pd
import sys
from os.path import abspath, join, dirname

sys.path.insert(0, join(abspath(dirname(__file__)), '..'))
from src.account import Account


class StrategyBase:
    df = None
    ctx = {}
    data_lookback_window = 1

    def __init__(self,
                 df: pd.DataFrame, data_lookback_window: int = 1):
        self.df = df
        self.data_lookback_window = data_lookback_window
        self.init_data(self.df)
        pass

    def init_data(self, df: pd.DataFrame):
        pass

    def simulate(self, start_day: str = '', end_day: str = '', init_amount: float = 100000.0):
        df = self.df.copy()
        ctx = self.ctx
        if start_day == '' and end_day == '':
            pass
        else:
            if end_day == '':
                df = df.loc[start_day:]
            else:
                df = df.loc[start_day:end_day]
        ctx['start_day'] = start_day
        ctx['end_day'] = end_day

        account = Account(init_amount=init_amount, start_date=start_day)

        for index in range(len(df)):
            if index < self.data_lookback_window:
                continue
            df_data = df.iloc[index - self.data_lookback_window:index + 1]
            self.run_strategy(df_data.tail(1)['trade_date'], df_data=df_data, account=account)
        return df

    def run_strategy(self, trade_day, df_data: pd.DataFrame, account: Account):
        pass
