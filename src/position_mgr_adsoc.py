import pandas as pd
import numpy as np
import json
from .position_mgr import PositionMgr


class PositionMgrAdsoc(PositionMgr):
    df = None
    stop_atr_factor = 2
    # df_i = None
    df_pos_record = None
    trade_detail = TradeDetail()

    account_risk = 0.01
    max_buy_cnt = 4

    trade_date = ''
    position_key = 0

    unit_account = 0
    position_day = 0  # update when change day
    unit_high_price = 0  # update when update called
    unit_cost = 0
    buy_cnt = 0
    add_prices = []
    stop_price = 0
    close_price = 0

    R = 0
    P_R = 0  # update when update called

    def __init__(self, account_risk=0.01, stop_atr_factor=2, max_buy_cnt=4):
        self.stop_atr_factor = stop_atr_factor
        self.account_risk = account_risk
        self.max_buy_cnt = max_buy_cnt
        super.__init__(self)

    def gen_new_df(self):
        df = pd.DataFrame(
            columns=[
                'trade_date',
                'position_key',
                'unit_account',
                'close_price',
                'unit_cost',
                'R',
                'P/R',
                'stop_price',
                'add_price',
                'position_day',
                'buy_cnt',
            ])
        return df

    def gen_pos_record(self):
        df = pd.DataFrame(
            columns=[
                'position_key',
                'unit_cost',
                'unit',
                'close_price',
                'profit',
                'W/L',
            ])
        return df

    def gen_pos_key(self):
        return self.position_key + 1

    def gen_add_prices(self, unit_price, atr):
        for i in range(4):
            factor = (i + 1) * 0.5
            add_price = unit_price + (atr * factor)
            self.add_prices.append(add_price)

    def open_position(self):
        self.position_key = self.gen_pos_key()
        self.buy_cnt = 0
        self.position_day = 0
        self.unit_account = 0
        self.unit_high_price = 0  # update when update called
        self.unit_cost = 0
        self.add_prices = []
        self.stop_price = 0
        self.close_price = 0
        # self.df_i = self.gen_new_df()

    def buy(self, trade_date: str, unit_price: float, atr: float, account):
        trade_amount = self.buy_mng(trade_date=trade_date, unit_price=unit_price, atr=atr, account=account)
        if trade_amount > 0:
            account.update(trade_date=trade_date, cash_change=-trade_amount, positionMgr=self)
        return trade_amount

    def buy_mng(self, trade_date: str, unit_price: float, atr: float, account):
        if self.buy_cnt >= self.max_buy_cnt:
            return 0

        if self.unit_high_price == 0:
            self.unit_high_price = unit_price

        self.trade_date = trade_date
        stop_price = 0

        # 每股风险
        R = atr * self.stop_atr_factor

        unit = np.floor(account.get_account_scale() * self.account_risk / R / 100) * 100

        if unit == 0:
            return 0

        buy_amount = unit_price * unit
        if not account.can_buy(buy_amount):
            return 0

        if self.unit_account == 0:
            self.open_position()
            self.gen_add_prices(unit_price=unit_price, atr=atr)

        self.trade_detail.trade_buy(trade_date=trade_date, position_key=self.position_key, trade_unit=unit,
                                    unit_price=unit_price)

        unit_cost = self.trade_detail.unit_cost(position_key=self.position_key)
        self.unit_high_price = max(unit_price, self.unit_high_price)
        stop_price = self.unit_high_price - self.stop_atr_factor * atr

        R = max(R, unit_cost - stop_price)

        self.R = max(self.R, R)
        self.unit_account = self.unit_account + unit
        self.unit_cost = unit_cost
        self.buy_cnt = self.buy_cnt + 1
        self.close_price = unit_price
        return buy_amount

    def remove_add_price(self):
        if len(self.add_prices) == 0:
            return

        self.add_prices.reverse()
        self.add_prices.pop()
        self.add_prices.reverse()

    def update(self, series_today: pd.Series):
        if self.unit_account == 0:
            return

        trade_date = series_today.trade_date
        if trade_date != self.trade_date:
            self.trade_date = trade_date

        profit = series_today.close - self.unit_cost
        self.unit_high_price = max(self.unit_high_price, series_today.high)
        self.P_R = profit / self.R
        self.stop_price = self.unit_high_price - self.stop_atr_factor * series_today.ATR
        self.close_price = series_today.close

        if self.position_day >= 20 \
                and series_today.MA17_trend < 0 \
                and series_today.MA25_trend < 0 \
                and series_today.MA17 < series_today.MA25:
            self.stop_price = series_today.MA17
        pass

    def day_start(self, trade_date: str):
        pass

    def day_end(self, trade_date: str):
        if self.unit_account == 0:
            return
        # # if self.df_i is None:
        #     return

        self.df = self.df.append(
            {
                'trade_date': self.trade_date,
                'position_key': self.position_key,
                'unit_account': self.unit_account,
                'close_price': self.close_price,
                'unit_cost': self.unit_cost,
                'R': self.R,
                'P/R': self.P_R,
                'stop_price': self.stop_price,
                'add_price': json.dumps(self.add_prices),
                'position_day': self.position_day,
                'buy_cnt': self.buy_cnt,
            },
            ignore_index=True
        )
        self.position_day += 1

    def close(self, trade_date: str, unit_price: float, account):
        trade_amount = self.close_mng(trade_date, unit_price, account)
        if trade_amount > 0:
            account.update(trade_date=trade_date, cash_change=trade_amount, positionMgr=self)

        return trade_amount

    def close_mng(self, trade_date: str, unit_price: float, account):
        trade_amount = self.unit_account * unit_price

        self.update_pos_record(position_key=self.position_key, unit_cost=self.unit_cost, close_price=unit_price,
                               unit=self.unit_account)
        self.trade_detail.trade_sell(trade_date, self.position_key, self.unit_account, unit_price)

        self.unit_account = 0
        self.buy_cnt = 0

        self.df = self.df.append(
            {
                'trade_date': trade_date,
                'position_key': self.position_key,
                'unit_account': self.unit_account
            },
            ignore_index=True,
        )

        # self.df = self.df.append(self.df_i, ignore_index=True)
        # self.df_i = None

        return trade_amount

    def update_pos_record(self, position_key: int, unit_cost: float, close_price: float, unit: int):
        profit = close_price - unit_cost
        W_L = 'W'
        if profit > 0:
            w_L = 'W'
        elif profit == 0:
            W_L = '-'
        else:
            W_L = 'L'
        self.df_pos_record = self.df_pos_record.append({
            'position_key': self.position_key,
            'W/L': W_L,
            'unit_cost': unit_cost,
            'close_price': close_price,
            'profit': close_price - unit_cost,
            'unit': unit
        }, ignore_index=True)

    # def get_current_risk(self):
    # if len(self.df_i) > 0:
    # return self.df.tail(1)[0]
    # else:
    #     return None

    def get_summary(self):
        return self.df

    def is_unit_empty(self):
        return self.unit_account == 0

    def position_value(self):
        return self.unit_account * self.close_price

    def to_excel(self, writer):
        self.df.to_excel(writer, sheet_name='position', index=False)
        self.df_pos_record.to_excel(writer, sheet_name='position_record', index=False)
        self.gen_position_report().to_excel(writer, sheet_name='position_report', index=False)
        self.trade_detail.to_excel(writer)

    def gen_position_report(self):
        # 交易次数
        trade_cnt = len(self.df_pos_record)
        # 胜率
        win_rate = len(self.df_pos_record.loc[self.df_pos_record['W/L'] == 'L']) / trade_cnt

        df_i = pd.DataFrame([
            (
                trade_cnt,
                win_rate
            )
        ],
            columns=[
                'trade_cnt',
                'win_rate',
            ])
        return df_i
