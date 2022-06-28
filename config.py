# change this when you actually use it 
SECRET = 'H7u0AgfhuGD7KIDhCsV5MFg8dK3R8BYYuU1TK59s' # Enter Your Secret Key Here
KEY = 'AK2ARY0LPA5ZO57IXO8Q' # This says api key id so idk if that is right
# if live trading
apiserver_domain = 'api.alpaca.markets'
# if paper
apiserver_domain = 'paper-api.alpaca.markets'
KEY = 'PKUAO4EHBUOR1PANLFPN'
SECRET = '3gEAUwCMMDooiJ92As3tqW1UsMURDFC5FyLzWrhM'
keys = {'APCA-API-KEY-ID' : KEY, 'APCA-API-SECRET-KEY' : SECRET}
BASE_URL = f'https://{apiserver_domain}/v2' # This is the base URL for paper trading
ACCOUNT_URL = f'{BASE_URL}/account'
DATA_URL = 'https://data.alpaca.markets/v2'
