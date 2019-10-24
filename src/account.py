import pandas as pd
import datetime
import numpy as np
from datetime import date
import sys
import math

from .position_mgr import PositionMgr


class Account:
    init_amount = 0
    df = None
    trade_date = ''
    total_assets = 0
    cash_balance = 0
    invest_assets = 0
    account_scale = 0
    fall_rate = 0
    max_total = 0
    profit_rate = 0
    max_fall_date = 0
    fall_day = 0
    log_return_rate = 0
    capital_av_rate = 0

    def __init__(self, init_amount: float = 100000):
        self.init_amount = init_amount
        self.df = pd.DataFrame(
            columns=[
                'trade_date',
                'total_assets',
                'cash_balance',
                'invest_assets',
                'account_scale',
                'max_total',
                'profit_rate',
                'fall_rate',
                'fall_day',
                'log_return_rate',
                'capital_av_rate'
            ])
        self.total_assets = init_amount
        self.cash_balance = init_amount
        self.invest_assets: float = 0.0
        self.account_scale = init_amount
        self.fall_day = 0

        # self.df.index = pd.to_datetime(self.df.trade_date)

    def gen_df_i(self, trade_date):
        df_i = pd.DataFrame([
            (trade_date,
             self.total_assets,
             self.cash_balance,
             self.invest_assets,
             self.account_scale,
             self.max_total,
             self.profit_rate,
             self.fall_rate,
             self.fall_day,
             self.log_return_rate,
             self.capital_av_rate
             )
        ],
            columns=[
                'trade_date',
                'total_assets',
                'cash_balance',
                'invest_assets',
                'account_scale',
                'max_total',
                'profit_rate',
                'fall_rate',
                'fall_day',
                'log_return_rate',
                'capital_av_rate'
            ])
        return df_i

    def update(self, trade_date: str, cash_change: float = 0, positionMgr: PositionMgr = None):
        self.cash_balance += cash_change

        if positionMgr is not None:
            self.invest_assets = positionMgr.position_value()

        self.total_assets = self.cash_balance + self.invest_assets

    def day_start(self, trade_date: str):
        self.trade_date = trade_date
        pass

    def day_end(self, trade_date: str):
        max_total = self.df['max_total'].max()
        if math.isnan(max_total):
            max_total = 0
        max_total = max(max_total, self.total_assets)

        fall_rate = (self.total_assets - max_total) / max_total
        profit_rate = (self.total_assets - self.init_amount) / self.init_amount

        self.max_total = max_total
        self.fall_rate = fall_rate
        self.profit_rate = profit_rate

        last_total_assets = 0
        if len(self.df) != 0:
            last_total_assets = self.df.tail(1).iloc[0]['total_assets']

        log_return_rate = np.nan
        if last_total_assets !=0 and self.total_assets != 0:
            log_return_rate = math.log(self.total_assets) - math.log(last_total_assets)

        self.log_return_rate = log_return_rate
        if self.fall_rate < 0:
            self.fall_day += 1
        else:
            self.fall_day = 0

        self.capital_av_rate = self.cash_balance / self.account_scale

        df_i = self.gen_df_i(trade_date)
        self.df = self.df.append(df_i, ignore_index=False, sort= False)

        pass

    def get_cash_balance(self):
        return self.cash_balance

    def can_buy(self, buy_amount: float):
        return self.cash_balance > buy_amount

    def to_excel(self, writer):
        self.df.to_excel(writer, sheet_name="account", index=False)
        self.gen_report().to_excel(writer,sheet_name="account_report", index=False)

    def get_account_scale(self):
        return self.account_scale

    def adjust_account_scale(self):
        self.account_scale = self.total_assets

    def gen_report(self):
        # 交易日
        trade_day_cnt = len(self.df)
        # 最大回撤
        max_fall_rate = self.df.fall_rate.min()
        # 最大回撤交易日旗数
        max_fall_day_cnt = self.df.fall_day.max()
        # 收益率
        profit_rate = self.df.tail(1).iloc[0].profit_rate
        # 对数收益率
        log_return_rate = self.df.log_return_rate.sum()
        # 每日对数收益率
        daily_log_return_rate = self.df.log_return_rate.mean()
        # 平均年化收益率
        year_log_return_rate = daily_log_return_rate * 250
        # 平均年化方差
        tmp = self.df.log_return_rate * 250
        year_log_return_rate_std = tmp.std()

        df_i = pd.DataFrame([
            (
                trade_day_cnt,
                max_fall_rate,
                max_fall_day_cnt,
                profit_rate,
                log_return_rate,
                daily_log_return_rate,
                year_log_return_rate,
                year_log_return_rate_std
            )
        ],
            columns=[
                'trade_day_cnt',
                'max_fall_rate',
                'max_fall_day_cnt',
                'profit_rate',
                'log_return_rate',
                'daily_log_return_rate',
                'year_log_return_rate',
                'year_log_return_rate_std'
            ])
        return df_i
