import sys
from os.path import abspath, join, dirname
sys.path.insert(0, join(abspath(dirname(__file__)), '..'))
print(sys.path)
from src.stock import Stock
import pandas as pd
sys.path.append("..")
tsStock = Stock()
keyword = '000001'
df = tsStock.get_daily_data(keyword,'2019-01-02','')
print (df)

# start_date = pd.to_datetime('20100101');
# print (start_date)
#
# print (start_date.strftime("%Y-%m-%d"))