import pandas as pd
import sys
from os.path import abspath, join, dirname

sys.path.insert(0, join(abspath(dirname(__file__)), '..'))
from src.account import Account
from src.position_mgr import PositionMgr


class StrategyBase:
    df = None
    ctx = {}
    data_lookback_window = 1

    def __init__(self,
                 df: pd.DataFrame,
                 data_lookback_window: int = 1,
                 ctx:dict = {}
                 ):
        self.df = df
        self.data_lookback_window = data_lookback_window
        self.ctx = ctx
        self.init_data(self.df)
        self.init_ctx(self.ctx)
        pass

    def init_data(self, df: pd.DataFrame):
        pass

    def init_ctx(self, ctx: dict):
        pass

    def simulate(self, start_day: str = '', end_day: str = '', init_amount: float = 100000.0,
                 positionMgr: PositionMgr = PositionMgr(), excel_path: str = None):
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

        account = Account(init_amount=init_amount)

        self.before_run(df)
        ctx['df'] = df

        for index in range(len(df)):
            if index < self.data_lookback_window:
                continue
            df_data = df.iloc[index - self.data_lookback_window:index + 1]
            trade_date = df_data.tail(1).iloc[0]['trade_date']
            account.day_start(trade_date=trade_date)
            positionMgr.day_start(trade_date=trade_date)

            self.run_strategy(trade_day=trade_date, df_day=df_data, account=account,
                              positionMgr=positionMgr, ctx=ctx)

            series_today = df_data.tail(1).iloc[0]
            positionMgr.update(series_today=series_today)
            account.update(trade_date=trade_date, cash_change=0, positionMgr=positionMgr)
            positionMgr.day_end(trade_date=trade_date)
            account.day_end(trade_date=trade_date)

        if excel_path is not None:
            self.write_excel(df=df, path=excel_path, account=account, positionMgr=positionMgr)

        return {
            'daily_data': df,
            'account': account.df,
            'account_report': account.gen_report(),
            'position': positionMgr.df,
            'position_record': positionMgr.df_pos_record,
            'position_report': positionMgr.gen_position_report(),
            'trade_detail': positionMgr.trade_detail.df
        }

    def write_excel(self, df: pd.DataFrame, path, account: Account, positionMgr: PositionMgr):
        writer = pd.ExcelWriter(path=path)
        df.to_excel(writer, sheet_name='daily_data', index=False)
        account.to_excel(writer)
        positionMgr.to_excel(writer)
        writer.save()

    def before_run(self, df: pd.DataFrame):
        pass

    def run_strategy(self, trade_day, df_day: pd.DataFrame, account: Account, positionMgr: PositionMgr,
                     ctx: dict = {}):
        pass
