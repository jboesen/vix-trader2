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

# initialize
is_open = True
# initialize current price queue
current_prices = deque([], maxlen=10)
# connect and authenticate to regular
account = json.loads(requests.get(ACCOUNT_URL, headers=keys).content)
# print(account)
if not account['status'] == 'ACTIVE':
    exit(1)
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


def trade(symbol):
    global trading
    trading = True
    r = requests.get(f"{BASE_URL}/account", headers=keys)
    cash = float(json.loads(r.text)['cash']) 
    print(f"cash: {cash}")
    
    # get vix price
    if is_open:
        global prev_order
        # get data from past year
        r = requests.get(f"{DATA_URL}/stocks/{symbol}/bars", params=payload, headers=keys)
        # we now have a list of bars
        # predict data for right now
        # print("got slope prediction")
        p = current_prices[-1]
        trading = False
        # TODO: change this as needed
        sleep(30)


def __main__():
    socket = "wss://stream.data.alpaca.markets/v2/iex"
    ws = websocket.WebSocketApp(socket, on_open=on_open, on_message=on_message)
    ws.run_forever()

if __name__ == '__main__':
    __main__()
