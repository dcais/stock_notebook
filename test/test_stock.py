from src.stock import Stock
import pandas as pd
tsStock = Stock()
keyword = '000001'
df = tsStock.get_daily_data(keyword,'2019-01-02','')
print (df)

# start_date = pd.to_datetime('20100101');
# print (start_date)
#
# print (start_date.strftime("%Y-%m-%d"))