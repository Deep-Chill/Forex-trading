import MetaTrader5 as mt5
import pandas as pd
import pytz
import sklearn as sk
from datetime import datetime, timedelta
import matplotlib as mpl
import matplotlib.pyplot as plt

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)

path = 'C:\Program Files\MetaTrader 5'
mt5.initialize(path)
mt5.initialize(login=, password='', server='')

### Important functions to remember ###
### symbol_info_tick() ###
### symbol_info() ###
### account_info() ###
### positions_get() ###

print("My current open positions: ")
usd_positions=mt5.positions_get(group="*USD*")
df = pd.DataFrame(list(usd_positions), columns=usd_positions[0]._asdict().keys())
print(df)
print("####################################################################\n")

### BELOW IS THE CODE TO SEND ORDERS TO THE MT5 TERMINAL ###
# request = {
#     "action": mt5.TRADE_ACTION_DEAL,
#     "symbol": "EURUSD",
#     "type": mt5.ORDER_TYPE_BUY,
#     "sl": 0.0,
#     "tp": 0.0,
#     "price": mt5.symbol_info_tick('EURUSD').ask,
#     "volume": 0.01,
#     "deviation": 20,
#     "magic": 12345,
#     "comment": "test",
#     "type_time": mt5.ORDER_TIME_GTC,
#     "type_filling": mt5.ORDER_FILLING_IOC,
# }
# order = mt5.order_send(request)
# print(order)

startdate = datetime(2020, 1, 1)
enddate = datetime.now()

Time_Frame = mt5.TIMEFRAME_M15
#I had to remove the "count" parameter in the copy_rates_range function for smaller timeframes. Not sure why it doesn't work. ###
eur_usd_rates_15 = mt5.copy_rates_range("EURUSD", Time_Frame, startdate, enddate)
# eur_usd_rates_4H = mt5.copy_rates_range("EURUSD", Time_Frame, startdate, enddate)

Rates = pd.DataFrame(eur_usd_rates_15)
Rates['time'] = pd.to_datetime(Rates['time'], unit='s')
Rates['SMA'] = Rates.close.rolling(100).mean()
Rates['SMA_position'] = 0

#if sma is above the current price, set the SMA_position to 0, else set it to 1
Rates.loc[Rates.SMA > Rates.close, 'SMA_position'] = 0
Rates.loc[Rates.SMA < Rates.close, 'SMA_position'] = 1

Rates['SMA_position'] = Rates['SMA_position'].fillna(0)
Rates['SMA_position'] = Rates['SMA_position'].astype(int)
Rates['SMA_position'] = Rates['SMA_position'].str.replace('0', 'SHORT')
Rates['SMA_position'] = Rates['SMA_position'].str.replace('1', 'LONG')

for i in range(len(Rates)):
    if i == 0:
        Rates.loc[i, 'size_of_profit'] = 0
    else:
        if Rates.loc[i, 'SMA_position'] == Rates.loc[i-1, 'SMA_position']:
            Rates.loc[i, 'size_of_profit'] = Rates.loc[i-1, 'size_of_profit'] + 1
        else:
            Rates.loc[i, 'size_of_profit'] = 0
k = 0
for i in range(len(Rates)):
    if i == 0:
        Rates.loc[i, 'size_of_profit_value'] = 0
    else:
        if Rates.loc[i, 'size_of_profit'] == 0:
            Rates.loc[i, 'size_of_profit_value'] = Rates.loc[i, 'close'] - Rates.loc[k, 'close']
            k = i
        else:
            # Rates.loc[i, 'size_of_profit_value'] = Rates.loc[i, 'close'] - Rates.loc[k, 'close']
            Rates.loc[i, 'size_of_profit_value'] = Rates.loc[i, 'close'] - Rates.loc[k, 'close']

print(Rates.columns)
#The following print shows the best rallies for the given timeframe
print(Rates.sort_values(by='size_of_profit_value', ascending=True).tail(100))
