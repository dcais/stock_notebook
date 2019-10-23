import pandas as pd
import datetime
from datetime import date


class Dec:
    amount = 0
    df = None

    def __init__(self, init_amount: float = 100000, start_date: str = ''):
        self.amount = init_amount
        if start_date == '':
            trade_date = date.today().strftime("%Y%m%d")
        self.df = pd.DataFrame(
            columns=['trade_date', 'total_assets', 'cash_balance', 'invest_assets', 'unit_account', 'trade_unit',
                     'trade_type',
                     'trade_unit_price', 'unit_close_price'])

        total_assets = init_amount
        cash_balance = init_amount
        invest_assets: float = 0.0
        unit_account = 0

        df_i = pd.DataFrame([(trade_date, init_amount, init_amount, invest_assets, unit_account)],
                            columns=['trade_date', 'total_assets', 'cash_balance', 'invest_assets', 'unit_account'])

        self.df = self.df.append(df_i, ignore_index=True, sort=False)
        self.df.index = pd.to_datetime(self.df.trade_date)
