import pandas as pd
import numpy as np
import json
from .position_mgr import PositionMgr


class PositionMgrAdosc(PositionMgr):
    stop_atr_factor = 2
    # df_i = None

    account_risk = 0.01
    max_buy_cnt = 4

    def __init__(self, account_risk=0.01, stop_atr_factor=2, max_buy_cnt=4):
        super(PositionMgrAdosc, self).__init__()
        self.stop_atr_factor = stop_atr_factor
        self.account_risk = account_risk
        self.max_buy_cnt = max_buy_cnt

    def gen_add_prices(self, unit_price, atr):
        for i in range(4):
            factor = (i + 1) * 0.5
            add_price = unit_price + (atr * factor)
            self.add_prices.append(add_price)

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

    def update_stop_price(self, series_today: pd.Series):
        self.stop_price = self.unit_high_price - self.stop_atr_factor * series_today.ATR
        if self.position_day >= 20 \
                and series_today.MA17_trend < 0 \
                and series_today.MA25_trend < 0 \
                and series_today.MA17 < series_today.MA25:
            self.stop_price = series_today.MA17
