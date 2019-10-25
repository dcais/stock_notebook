import talib
import math

def HMA(series, period):
    half_period = int(period/2)
    sqrt_period = int(math.sqrt(period))

    series_WMA_half = talib.WMA(series,half_period)
    series_WMA = talib.WMA(series,period)

    tmp =  series_WMA_half * 2 - series_WMA
    return talib.WMA(tmp,sqrt_period)

