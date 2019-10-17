import pandas as pd
import re
import requests

class SinaStock:
    x_client = None
    stock_df = None

    def __init__(self):
        pass

    def get_sina_code(self, code):
        tmp = code.split('.')
        sinaCode = tmp[1].lower() + tmp[0]
        return sinaCode

    def get_realtime(self, code):
        sinaCode = self.get_sina_code(code)
        params = {
            'list': sinaCode
        }
        r = requests.get('http://hq.sinajs.cn/', params=params)
        tmp = re.sub(r'^var.*="', r'', r.text)
        tmp = re.sub(r'";\n$', r'', tmp)
        strs = tmp.split(',')
        stock_rt = {
            'ts_code': code,
            'open': float(strs[1]),
            'pre_close': float(strs[2]),
            'close': float(strs[3]),
            'high': float(strs[4]),
            'low': float(strs[5]),
            'vol': float(strs[8]) / 100,
            'amount': float(strs[9]) / 1000,
            'trade_date': strs[30].replace('-', ''),
            'trade_time': strs[31]
        }
        df=pd.DataFrame(stock_rt,index=[0])
        df.index = pd.to_datetime(df.trade_date)
        return df
