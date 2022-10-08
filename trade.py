#%%
import datetime as dt
from IPython.display import display
import json
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import requests.api
import websocket
from collections import deque
from sklearn.linear_model import LinearRegression
from threading import Thread
from time import sleep
from config import *
from scipy.stats import norm

STD = 5.511435523209041
MEAN = 22.671190456349215
# initialize
is_open = True
# initialize current price queue
current_prices = deque([], maxlen=10)
# connect and authenticate to regular
account = json.loads(requests.get(ACCOUNT_URL, headers=keys).content)
# print(account)
if not account['status'] == 'ACTIVE':
    exit(1)
# 1 = longing, 2 = shorting, 3 = hard shorting
prev_order = ''
# Prevent trying to trade before the previous trade is done
trading = False

def on_open(ws):
    print("opened")
    login = {'action': 'auth', 'key': f'{KEY}', 'secret': f'{SECRET}'}
    ws.send(json.dumps(login))
    # one-minute bars
    listen_message = {'action': 'subscribe', 'bars':['VIX']}
    ws.send(json.dumps(listen_message))


def on_message(ws, message):
    print(message)
    bar = json.loads(message)[0]
    avg = (bar['o'] + bar['l']) / 2
    current_prices.append(avg)
    print(f"trading: {trading}")
    if not trading:
        Thread(target=trade, args=("VXX", )).start()


def liquidate():
    # cancel open orders
    print("liquidating")
    open_orders = requests.get(f"{BASE_URL}/orders", headers=keys).text
    if open_orders:
        requests.delete(f"{BASE_URL}/orders", headers=keys)
    # get all positions
    positions = json.loads(requests.get(f"{BASE_URL}/positions", headers=keys).text)
    df = pd.DataFrame(positions)
    # is this the right way to iterate?
    for r in df.to_dict(orient="records"):
        if r['side'] == 'long':
            print(f"selling {r['symbol']}")
            payload = {
                'symbol' : r['symbol'],
                'qty' : r['qty'],
                'side' : 'sell',
                'type' : 'market', 
                'time_in_force' : 'day',
            }
            requests.post(f"{BASE_URL}/orders", headers=keys, json=payload)
        if r['side'] == 'short':
            print(f"buying {r['symbol']}")
            payload = {
                'symbol' : r['symbol'],
                'qty' : r['qty'],
                'side' : 'buy',
                'type' : 'market', 
                'time_in_force' : 'day',
            }
            requests.post(f"{BASE_URL}/orders", headers=keys, json=payload)
            # print(receipt.text)
    for i in range(5):
        sleep(2)
        positions = json.loads(requests.get(f"{BASE_URL}/positions", headers=keys).text)
        print(positions)
        if not positions:
            print("liquidating successful")
            return
    # restart
    print("calling main")
    __main__()


def trade(symbol):
    print("top of trade")
    global trading
    trading = True
    r = requests.get(f"{BASE_URL}/account", headers=keys)
    # store cash for later
    cash = float(json.loads(r.text)['cash']) 
    print(f"cash: {cash}")
    print("done checking on account...")
    
    # get vix price
    if is_open:
        global prev_order
        # get data from past year
        r = requests.get(f"{DATA_URL}/stocks/{symbol}/bars", params=payload, headers=keys)
        # we now have a list of bars

        # predict data for right now
        # print("got slope prediction")
        p = current_prices[-1]

        percentile = norm.cdf(p, loc=MEAN, scale=STD)
        above_threshold = percentile > .75
        below_threshold = percentile < .25

        if above_threshold and prev_order != 'vix short':
            print("going for short...")
            liquidate()
            payload = {
                'symbol' : 'XSD',
                'notional' : cash,
                'side' : 'buy',
                'type' : 'market', 
                'time_in_force' : 'day',
                }
            order = requests.post(f"{BASE_URL}/orders", headers=keys, json=payload)
            # print(order.text)
            prev_order = 'vix short'
            trading = False
            return
        # if current price is below predicted, long it
        # I have no idea here, but this would be assuming low price regresses to the mean within a day
        # (4 15-min intervals/hour * 8 hours/day)
        if below_threshold and prev_order != 'vix long':
            print("going long")
            liquidate()
            payload = {
                'symbol' : 'VXX',
                'notional' : str(cash),
                'side' : 'buy',
                'type' : 'market', 
                'time_in_force' : 'day',
                }
            order = requests.post(f"{BASE_URL}/orders", headers=keys, json=payload)
            # print(order.text)
            prev_order = 'vix long'
            trading = False
            return

        if prev_order != 'general long':
            print("chillin w voo")
            liquidate()
            payload = {
                'symbol' : 'VOO',
                'notional' : str(cash),
                'side' : 'buy',
                'type' : 'market', 
                'time_in_force' : 'day',
                }
            order = requests.post(f"{BASE_URL}/orders", headers=keys, json=payload)
            # print(order.text)
            prev_order = 'general long'
            trading = False
            return
        print("Chilling because none of the conditions were met")
        trading = False
        # TODO: change this as needed
        sleep(30)


def __main__():
    socket = "wss://stream.data.alpaca.markets/v2/iex"
    ws = websocket.WebSocketApp(socket, on_open=on_open, on_message=on_message)
    ws.run_forever()

if __name__ == '__main__':
    __main__()
