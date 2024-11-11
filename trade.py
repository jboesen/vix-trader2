import json
import requests
import websocket
import pandas as pd
from collections import deque
from threading import Thread
from time import sleep
from scipy.stats import norm
from config import KEY, SECRET, ACCOUNT_URL, BASE_URL, DATA_URL, keys

# Constants for statistical calculations
STD = 5.511435523209041
MEAN = 22.671190456349215

# Initialize variables
is_market_open = True
current_prices = deque(maxlen=10)
prev_order = ''
trading = False

# Authenticate the account
response = requests.get(ACCOUNT_URL, headers=keys)
account = response.json()
if account.get('status') != 'ACTIVE':
    print("Account is not active. Exiting.")
    exit(1)

def on_open(ws):
    login_message = {
        'action': 'auth',
        'key': KEY,
        'secret': SECRET
    }
    ws.send(json.dumps(login_message))
    subscribe_message = {
        'action': 'subscribe',
        'bars': ['VIX']
    }
    ws.send(json.dumps(subscribe_message))

def on_message(ws, message):
    global current_prices
    global trading
    try:
        data = json.loads(message)
        if data and isinstance(data, list):
            bar = data[0]
            avg_price = (bar.get('o', 0) + bar.get('l', 0)) / 2
            current_prices.append(avg_price)
            if not trading:
                Thread(target=trade, args=("VXX",)).start()
    except Exception as e:
        print(f"Error processing message: {e}")

def liquidate():
    print("Liquidating positions...")
    # Cancel open orders
    open_orders_response = requests.get(f"{BASE_URL}/orders", headers=keys)
    open_orders = open_orders_response.json()
    if open_orders:
        requests.delete(f"{BASE_URL}/orders", headers=keys)

    # Get all positions
    positions_response = requests.get(f"{BASE_URL}/positions", headers=keys)
    positions = positions_response.json()
    if positions:
        for position in positions:
            side = position.get('side')
            symbol = position.get('symbol')
            qty = position.get('qty')
            if side == 'long':
                print(f"Selling {symbol}")
                submit_order(symbol, qty, 'sell')
            elif side == 'short':
                print(f"Buying {symbol}")
                submit_order(symbol, qty, 'buy')

    # Wait until all positions are liquidated
    for _ in range(5):
        sleep(2)
        positions_response = requests.get(f"{BASE_URL}/positions", headers=keys)
        positions = positions_response.json()
        if not positions:
            print("Liquidation successful")
            return
    print("Positions not fully liquidated, attempting again")

def submit_order(symbol, qty, side):
    order_payload = {
        'symbol': symbol,
        'qty': qty,
        'side': side,
        'type': 'market',
        'time_in_force': 'day'
    }
    response = requests.post(f"{BASE_URL}/orders", headers=keys, json=order_payload)
    print(f"Order response: {response.text}")

def submit_notional_order(symbol, notional, side):
    order_payload = {
        'symbol': symbol,
        'notional': str(notional),
        'side': side,
        'type': 'market',
        'time_in_force': 'day'
    }
    response = requests.post(f"{BASE_URL}/orders", headers=keys, json=order_payload)
    print(f"Order response: {response.text}")

def trade(symbol):
    global trading
    global prev_order
    trading = True
    print("Starting trade process...")

    # Get account cash balance
    account_response = requests.get(f"{BASE_URL}/account", headers=keys)
    account_data = account_response.json()
    cash = float(account_data.get('cash', 0))
    print(f"Available cash: {cash}")

    if is_market_open and current_prices:
        latest_price = current_prices[-1]
        percentile = norm.cdf(latest_price, loc=MEAN, scale=STD)
        above_threshold = percentile > 0.75
        below_threshold = percentile < 0.25

        if above_threshold and prev_order != 'vix short':
            liquidate()
            submit_notional_order('XSD', cash, 'buy')
            prev_order = 'vix short'
            trading = False
            return

        elif below_threshold and prev_order != 'vix long':
            print("Executing VIX long position")
            liquidate()
            submit_notional_order('VXX', cash, 'buy')
            prev_order = 'vix long'
            trading = False
            return

        elif prev_order != 'general long':
            liquidate()
            submit_notional_order('VOO', cash, 'buy')
            prev_order = 'general long'
            trading = False
            return

    trading = False

def __main__():
    socket = "wss://stream.data.alpaca.markets/v2/iex"
    ws = websocket.WebSocketApp(socket, on_open=on_open, on_message=on_message)
    ws.run_forever()

if __name__ == '__main__':
    __main__()
