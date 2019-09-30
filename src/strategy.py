import pandas as pd
import talib as talib
import numpy as np


class FirstStrategy:
    code = ''
    start_date = ''
    end_date = ''
    df = None
    stock_info = None
    prev = None

    def __init__(self, stock, stock_keyword, start_date='', end_date='', sma_periods=[99, 145]):
        self.stock_info = stock.get_stock_info(stock_keyword)
        df = stock.get_daily_data(stock_keyword, start_date, end_date)
        if df is None:
            return
        df['sar'] = talib.SAR(df.high, df.low, acceleration=0.1, maximum=2)
        df['ATR'] = talib.ATR(df.high, df.low, df.close, timeperiod=25)
        df['macd_dif'], df['macd_dem'], df['macd_ocr'] = talib.MACD(df.close, 12, 26, 9)
        for period in sma_periods:
            name = "SMA" + str(period)
            sma = talib.SMA(np.array(df.close), period)
            df[name] = sma
        self.df = df

    def simulate(self, start_date, end_date='', init_amount=100000, account_risk=0.01, stop_price_factor=2.5,
                 max_add_count=4):
        if self.df is None:
            return None

        df = self.df.copy()
        if end_date == '':
            df = df.loc[start_date:]
        else:
            df = df.loc[start_date:end_date]

        if len(df) == 0 :
            return None

        df.loc[:, 'signal'] = np.array([''] * len(df))
        df.loc[:, 'account'] = np.array([float(0)] * len(df))
        df.loc[:, 'balance'] = np.array([float(0)] * len(df))
        df.loc[:, 'action'] = np.array([''] * len(df))
        df.at[df.index[0], 'account'] = init_amount
        df.at[df.index[0], 'balance'] = init_amount
        # init unit
        df.loc[:, 'unit'] = np.array([float(0)] * len(df))
        df.loc[:, 'unit_price'] = np.array([float(0)] * len(df))
        df.loc[:, 'unit_account'] = np.array([float(0)] * len(df))
        df.loc[:, 'unit_value'] = np.array([float(0)] * len(df))
        df.loc[:, 'unit_high'] = np.array([float(0)] * len(df))
        df.loc[:, 'stop_price'] = np.array([float(0)] * len(df))
        df.loc[:, 'unit_cost'] = np.array([float(0)] * len(df))
        df.loc[:, 'R'] = np.array([float(0)] * len(df))
        df.loc[:, 'P/R'] = np.array([float(0)] * len(df))
        df.loc[:, 'add_price'] = np.array([float(0)] * len(df))
        df.loc[:, 'buy_count'] = np.array([float(0)] * len(df))

        r_df = df.apply(self.run_strategy,axis=1,args =(start_date,end_date, init_amount, account_risk , stop_price_factor,  max_add_count))
        return r_df

    def stragyty_determine_buy_signal_1(self,prev, cur):
        signal = ""
        sma_f = 'SMA99'
        sma_s = 'SMA145'
        cond2 = cur[sma_f] > cur[sma_s]  # and cur[sma_f] > prev[sma_f] #and cur[sma_s] > prev[sma_s]
        cond1 = cur['unit_account'] == 0 and cur['close'] > cur['sar']
        # cond_macd = cur[''macd_ocr] > 0

        if cond1 and cond2 and prev['unit_account'] == 0:
            signal = 'pre_buy'
        return signal;

    def stragyty_calc_buy(self, prev, cur, init_account, account_risk, stop_atr_factor, max_add_count=0):
        signal = None
        action = ''
        unit = unit_price = unit_cost = stop_price = R = None

        add = False
        add_price = 0
        add_cond1 = prev['unit_account'] > 0 and prev['add_price'] < cur['high'] and prev['add_price'] > 0
        # and_cond2 = prev['sar_stop_price'] < prev['close']

        signal = self.stragyty_determine_buy_signal_1(prev, cur)

        if prev['signal'] == 'pre_buy' and prev['unit_account'] == 0:
            action = 'buy'
            # 以开盘价买入
            unit_price = cur['open']


        elif add_cond1 and prev['buy_count'] < max_add_count:
            action = 'buy'
            add = True
            if cur['add_price'] < cur['low']:
                unit_price = cur['open']
            else:
                unit_price = prev['add_price']

        if action == 'buy':
            buy_count = prev['buy_count'] + 1
            stop_price = unit_price - stop_atr_factor * cur['ATR']

            if add:
                R = prev['R']
                tmpR = unit_price - stop_price
                unit = np.round(init_account * account_risk / R / 100) * 100
            else:
                R = unit_price - stop_price
                unit = np.round(init_account * account_risk / R / 100) * 100

            unit_cost = (prev['unit_account'] * prev['unit_cost'] + unit_price * unit) / (unit + prev['unit_account'])
            add_price = unit_price + 0.5 * prev['ATR']

            if prev['account'] < unit_price * unit or unit == 0:
                add = False
                signal = ""
                action = ""
                unit = 0
                unit_price = 0
                unit_cost = 0
                stop_price = 0
                add_price = 0
            else:
                cur['buy_count'] = buy_count
        else:
            cur['buy_count'] = prev['buy_count']

        return signal, action, unit, unit_price, unit_cost, stop_price, R, add_price, add

    def stragyty_calc_sell(self,prev, cur):
        signal = None
        action = ''
        unit = unit_price = None
        sma_f = 'SMA17'
        sma_s = 'SMA25'
        # cond2 = cur[sma_f] < cur[sma_s] and cur[sma_f] < prev[sma_f] and cur[sma_s] < prev[sma_s]
        if prev['unit_account'] > 0:
            #         stop_price = prev['stop_price'] if prev['stop_price'] > prev['sar_stop_price'] else prev['sar_stop_price']
            #         if stop_price > prev['close']:
            stop_price = prev['stop_price']
            # 铁定要卖出
            if cur['low'] < stop_price:
                action = 'sell'
                unit = 0 - prev['unit_account']

                unit_price = stop_price
            #         elif cond2:
            #             signal = 'pre_sell'
            elif prev['signal'] == 'pre_sell':
                action = 'sell'
                unit = 0 - prev['unit_account']
                unit_price = cur['open']

        return signal,action, unit, unit_price

    def stragyty_calc_pr(self,prev, cur):
        PdR = P = R = unit_cost = None
        if cur['unit_account'] > 0:
            unit_cost = cur['unit_cost']
            if unit_cost == 0:
                unit_cost = prev['unit_cost']

            R = cur['R']
            if R == 0:
                R = prev['R']
            P = cur['close'] - unit_cost
            PdR = P / R
        else:
            if cur['action'] == 'sell':
                unit_cost = prev['unit_cost']
                R = prev['R']
                P = cur['unit_price'] - unit_cost
                PdR = P / R
        return unit_cost, R, P, PdR

    def run_strategy(self, cur, simu_start_date, simu_end_date, init_amount, account_risk, stop_price_factor,
                     max_add_count):
        prev = self.prev
        if prev is None:
            self.prev = cur.copy()
            return cur
        if prev['trade_date'] == cur['trade_date']:
            self.prev = cur.copy()
            return cur

        if not self.is_exec_strategye(prev, cur, simu_start_date, simu_end_date):
            cur['account'] = prev['account']
            cur['balance'] = prev['balance']
            self.prev = cur.copy()
            return cur

        signal,action, unit, unit_price,\
        unit_cost, stop_price, R,\
        add_price, add = self.stragyty_calc_buy(prev, cur, init_amount,account_risk,stop_price_factor, max_add_count)
        if signal is not None:
            cur['signal'] = signal
        if action is not None:
            cur['action'] = action
        if action == 'buy':
            cur['action'] = action
            cur['unit'] = unit
            cur['unit_price'] = unit_price
            cur['unit_cost'] = unit_cost
            cur['stop_price'] = stop_price
            cur['R'] = R

        cur['add_price'] = add_price
        if cur['add_price'] == 0:
            cur['add_price'] = prev['add_price']

        signal, action, unit, unit_price = self.stragyty_calc_sell(prev, cur)

        if signal is not None:
            cur['signal'] = signal

        if action == 'sell':
            cur['action'] = action
            cur['unit'] = unit
            cur['unit_price'] = unit_price
            cur['add_price'] = 0
            cur['buy_count'] = 0

        cur['unit_account'] = prev['unit_account'] + cur['unit']
        unit_cost, R, P, PdR = self.stragyty_calc_pr(prev, cur)

        if unit_cost is not None:
            cur['unit_cost'] = unit_cost
            cur['R'] = R
            cur['P/R'] = PdR

        if cur['unit_account'] > 0:
            if prev['unit_account'] > 0:
                cur['unit_high'] = cur['high'] if cur['high'] > prev['unit_high'] else prev['unit_high']
            else:
                cur['unit_high'] = cur['high']
        else:
            cur['unit_high'] = 0

        if cur['unit_account'] > 0 and ( cur['action'] != "buy" or add ):
            cur['stop_price'] = cur['unit_high'] - cur['ATR'] * stop_price_factor

        cur['account'] = prev['account'] - cur['unit'] * cur['unit_price']
        cur['unit_value'] = cur['unit_account'] * cur['close']
        cur['balance'] = cur['unit_value'] + cur['account']

        self.prev = cur.copy()

        return cur

    def is_exec_strategye(self, prev, cur, start_date, end_date=''):
        if prev is None:
            return False
        if pd.isna(prev['ATR']):
            return False
        if pd.to_datetime(cur['trade_date']) < pd.to_datetime(start_date):
            return False

        if end_date != '' and pd.to_datetime(cur['trade_date']) > pd.to_datetime(end_date):
            return False
        return True
