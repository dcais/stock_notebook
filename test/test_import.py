from src.ts_stock import TsStock
tsStock = TsStock()
keyword = '上证综指'
df = tsStock.getDailyData(keyword,'20120101','')
print (df)