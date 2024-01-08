import websocket
import json
from binance.client import Client
from talib import abstract
import pandas as pd

import websocket
import json
from binance.client import Client
from talib import abstract
import pandas as pd

class TradingBot:
    def __init__(self, api_key, api_secret, trading_symbol, leverage, risk_reward_ratio):
        self.api_key = api_key
        self.api_secret = api_secret
        self.trading_symbol = trading_symbol
        self.leverage = leverage
        self.rrr = risk_reward_ratio
        self.client = Client(api_key, api_secret)
        self.df_final = None
        self.entry_price = 0.00
        self.exit_price = 0.00
        self.demo_acc = 10000
        self.tp = 0
        self.sell_big_profit = 0
        self.stoploss = 0
        self.profit_loss = 0

    def set_initial_balance(self):
        start_balance = self.client.futures_account_balance()
        initial_balance = start_balance[0]['balance']
        print("================================")
        print('Initial balance:  {}'.format(initial_balance))
        print("================================")

    def set_leverage(self):
        change_leverage = self.client.futures_change_leverage(symbol=self.trading_symbol, leverage=self.leverage)
        print('Leverage set to: ', change_leverage['leverage'])

    def fetch_history_data(self):
        history_data = self.client.futures_klines(symbol=self.trading_symbol, interval=self.client.KLINE_INTERVAL_5MINUTE, limit=200)
        columns = ['T', 'O', 'H', 'L', 'C', 'V', 'KC', 'QV', 'NT', 'TBA', 'TBQ', 'E']
        self.df_final = pd.DataFrame(history_data, columns=columns)
        self.df_final= self.df_final.drop(self.df_final.tail(1).index)
        self.df_final['T'] = pd.to_datetime(self.df_final['T'], unit='ms')
        self.df_final['EMA'] = abstract.EMA(self.df_final['C'], timeperiod=5)
        print(self.df_final.tail(5))
        print(type(self.df_final))

    def on_message(self, ws, message):
        data = json.loads(message)
        candel = data['k']
        L_Time = data['E']
        open_data = float(candel['o'])
        candel_closing = candel['x']
        high_data = float(candel['h'])
        low_data = float(candel['l'])
        closing_data = float(candel['c'])


    def on_error(self, ws, error):
        print(f"WebSocket Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print("Closed")

    def on_open(self, ws):
        print("Connected")
        print('Receiving Data...')
        print("Waiting for Signal")

    def connect_websocket(self):
        websocket_url = f'wss://fstream3.binance.com/ws/{self.trading_symbol.lower()}@kline_5m'
        ws = websocket.WebSocketApp(websocket_url) 
        ws.on_open=self.on_open 
        ws.on_message=self.on_message 
        ws.on_error=self.on_error 
        ws.on_close=self.on_close
        ws.run_forever()

    def run_trading_strategy(self):
        # Your trading strategy logic here
        pass

if __name__ == "__main__":
    # Replace these with your actual API key and secret
    api_key = 'BwtkmrnTu9U2r1gjdy5gwtv3s8s82QR0kEt130MBNWLDMcImeJHU6Af8fyYpF7AN'
    api_secret = '9rJYUHzOrXnYdGY0dnsZwvcnmOVtrN1p8cHZwOtVeaAqRniY23A89Y8oMBRzeacF'
    Trading_SYMBOL = 'BTCUSDT'

    # Initialize the trading bot
    trading_bot = TradingBot(api_key, api_secret, Trading_SYMBOL, 100, 2)

    # Set initial balance and leverage
    # trading_bot.set_initial_balance()
    # trading_bot.set_leverage()

    # # Fetch historical data
    trading_bot.fetch_history_data()

   
    # Connect to WebSocket and start trading strategy
    # trading_bot.connect_websocket()
    # trading_bot.run_trading_strategy()

