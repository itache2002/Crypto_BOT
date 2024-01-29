import websocket
import json
from binance.client import Client
import pandas as pd
from binance.client import Client
from binance.enums import *
from talib import abstract
import numpy as np

# This api is for Mainnet.
api_key = 'API_KEY'
api_secret ='api_secret'

#This api is for Testnet.
# api_key ='81d645dfd37d146787b05f364d07cdb0e1866112d60efd40240cdd0eea13ae0f'
# api_secret='eacebd7a032d0db1e7c11b1fda87cc8c2842c4a44410d3dd4170968eda3ed62a'

Trading_SYMBOL='BTCUSDT'

client = Client( api_key, api_secret) 
Lev = 100 #leverage settings
rrr = 2 #risk reward ratio
risk = 4.25 #risk percent drop from initial balance stops the bot

# Set the trading symbol and interval
symbol = 'btcusdt'
interval = '5m'
EMA = 5
entry_price=0.00
exit_price = 0.00
Demo_acc= 10000
tp = 0 
sell_big_profit=0
Stoploss = 0 
profit_loss =0
TakePTofit=0
# Binance WebSocket URL for Kline/Candlestick data
# websocket_url = f"wss://stream.binancefuture.com/ws/{symbol.lower()}@kline_{interval}" #for testnet market 
futures_websocket = 'wss://fstream3.binance.com/ws/{}@kline_{}'.format(symbol, interval)# for live markert data
start_balance = client.futures_account_balance()
initial_balance = start_balance[0]['balance']
print("================================")
print('Initial balance:  {}'.format(initial_balance))
print("================================")

# lev=int(input("Enter the Leverage to use"))
change_leverage = client.futures_change_leverage(symbol=Trading_SYMBOL, leverage=Lev)
print('Leverage set to: ', change_leverage['leverage'])


history_Data= client.futures_klines(symbol=Trading_SYMBOL,interval=client.KLINE_INTERVAL_5MINUTE,limit=100)
columns = ['T', 'O', 'H', 'L', 'C', 'V', 'KC', 'QV', 'NT', 'TBA', 'TBQ', 'E']
H_data = pd.DataFrame(history_Data, columns=columns)
H_edit_data = H_data.drop(['V', 'KC', 'QV', 'NT', 'TBA', 'TBQ', 'E'], axis=1)
df_final = H_edit_data.drop(H_edit_data.tail(1).index)
df_final['T']= pd.to_datetime(df_final['T'],unit='ms')
df_final['EMA']= abstract.EMA(df_final['C'],timeperiod= EMA)

def on_message(ws, message):

    global df_final , Demo_acc, entry_price, tralling_ST,  profit_loss, exit_price,tp,sell_big_profit,Stoploss,TakePTofit
    try:
        data = json.loads(message)
        candel= data['k']
        L_Time = data['E']
        open_data = float(candel['o'])
        candel_closing = candel['x']
        high_data = float(candel['h'])
        low_data = float(candel['l'])
        closing_data = float(candel['c'])
        pre_Data = df_final.iloc[-1] 
        last_close=float(pre_Data['C'])
        last_open =float(pre_Data['O'])
        last_low= float(pre_Data['L'])
        last_high=float(pre_Data['H'])
        is_Red =pre_Data['C']< pre_Data['O']
        if candel_closing:
            new_data = pd.DataFrame({
                'T': [pd.to_datetime(L_Time).strftime('%Y-%m-%d %H:%M:%S')],
                'O': [open_data],
                'H': [high_data],
                'L': [low_data],
                'C': [closing_data] })
#             new_data['T']= pd.to_datetime(new_data['T'], unit='ms')
            df_final = pd.concat([df_final, new_data], ignore_index=True)
            df_final['EMA']=abstract.EMA(df_final['C'] ,EMA)
#           print(df_final)
        #Sell Condition
        if is_Red and float(last_low> pre_Data['EMA']):
#             if float(position_amount) == 0:
                print('##################################')
                print('SELL SIGNAL IS ON! Executing order')
                print('##################################')
                print("=========================================================")
                
                entry_price= last_close
                entry_price = (round(entry_price,2))
                print("Entry Price at: {}".format(entry_price))  
                sl = last_high
                Stoploss=(round(sl,2))
                print("Calculated stop loss at: {}".format(Stoploss))
#               take_profit = (entry_price - (rrr * (stop_loss - entry_price)))
                take_profit = entry_price - 60
                sell_big_profit = entry_price -100
                tp = (round(take_profit , 2))
                print("Calculated Take profit at:{}".format(tp))
        if closing_data == tp:
            print("Profit Half quantity sole")
            exit_price = closing_data
            print("Half exit",exit_price)
        if closing_data == sell_big_profit:
            print("Sell side 100 points hit ")
            exit_price = closing_data
            print("100 points exit",)
        elif closing_data == Stoploss:
            print("Loss stoploss was hit")
            exit_price =  closing_data
            print("Short side loss exit_price :",exit_price)
            Stoploss = 0 
            tp=0
        profit_loss = exit_price - entry_price
        if profit_loss < 0:
            print("profit")
            add_entry_to_excel(pd.to_datetime(L_Time, unit='ms').floor('T'), entry_price, exit_price, profit_loss, Demo_acc,tp,Stoploss)
            Demo_acc += 200
            print("The finel balance ", Demo_acc)
        elif profit_loss > 0:
            print("Loss")
            Demo_acc -= 170
            add_entry_to_excel(pd.to_datetime(L_Time, unit='ms').floor('T'), entry_price, exit_price, profit_loss, Demo_acc,tp,Stoploss)
            print("The finel balance ", Demo_acc)
#                 sell_limit_order = client.futures_create_order(symbol=TRADE_SYMBOL, side='SELL', type='LIMIT', timeInForce='GTC', price=entry_price, quantity=TRADE_QUANTITY)
#                 order_id = sell_limit_order['orderId']
#                 order_status = sell_limit_order['status']

#                 while order_status != 'FILLED':
#                         time.sleep(10) #check every 10sec if limit order has been filled
#                         order_status = client.futures_get_order(symbol=TRADE_SYMBOL, orderId=order_id)['status']
#                         print(order_status)

#                         if order_status == 'FILLED':
#                             time.sleep(1)
#                             set_stop_loss = client.futures_create_order(symbol=TRADE_SYMBOL, side='BUY', type='STOP_MARKET', quantity=TRADE_QUANTITY, stopPrice=stop_loss)
#                             time.sleep(1)
#                             set_take_profit = client.futures_create_order(symbol=TRADE_SYMBOL, side='BUY', type='TAKE_PROFIT_MARKET', quantity=TRADE_QUANTITY, stopPrice=take_profit)
#                             break

#                         if time.time() > timeout:
#                             order_status = client.futures_get_order(symbol=TRADE_SYMBOL, orderId=order_id)['status']
                            
#                             if order_status == 'PARTIALLY_FILLED':
#                                 cancel_order = client.futures_cancel_order(symbol=TRADE_SYMBOL, orderId=order_id)
#                                 time.sleep(1)
                                
#                                 pos_size = client.futures_position_information()
#                                 df = pd.DataFrame(pos_size)
#                                 pos_amount = abs(float(df.loc[SYMBOL_POS, 'positionAmt']))

#                                 time.sleep(1)
#                                 set_stop_loss = client.futures_create_order(symbol=TRADE_SYMBOL, side='BUY', type='STOP_MARKET', quantity=pos_amount, stopPrice=stop_loss)
#                                 time.sleep(1)
#                                 set_take_profit = client.futures_create_order(symbol=TRADE_SYMBOL, side='BUY', type='TAKE_PROFIT_MARKET', quantity=pos_amount, stopPrice=take_profit)
#                                 break
                            
#                             else:
#                                 cancel_order = client.futures_cancel_order(symbol=TRADE_SYMBOL, orderId=order_id)
#                                 break

                
    except Exception as e:
        print(f"Error: {e}")
#         print(f"Raw Message: {message}")

def on_error(ws, error):
    print(f"WebSocket Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("Closed")

def on_open(ws):
    print("Connected")
    print('Receiving Data...')
    print("Waiting for Signal")

# Create WebSocket connection
ws = websocket.WebSocketApp(futures_websocket, on_open=on_open, on_message=on_message, on_error=on_error, on_close=on_close)
ws.run_forever()
