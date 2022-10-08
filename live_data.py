import websocket, json
from config import *
from trade import trade
from queue import Queue

current_price = Queue(maxsize = 10)
# TODO: debug this
def on_open(ws):
    print("opened")
    login = {'action': 'auth', 'key': f'{KEY}', 'secret': f'{SECRET}'}
    ws.send(json.dumps(login))
    # one-minute bars
    listen_message = {'action': 'subscribe', 'bars':['VXX']}
    ws.send(json.dumps(listen_message))

def on_message(ws, message):
    bar = json.loads(message.text)
    avg = (bar['o'] + bar['l']) / 2
    current_price.put(avg)


socket = "wss://stream.data.alpaca.markets/v2/iex"
ws = websocket.WebSocketApp(socket, on_open=on_open, on_message=trade)
ws.run_forever()
pass
