import requests

IEX_API_KEY = "xuYzdGAVupa00wAqchtpGb0D0NMjsHIy"

def get_stock_price(symbol):
    base_url = f'https://cloud.iexapis.com/stable/stock{symbol}/quote?token={IEX_API_KEY}'
    response = requests.get(base_url)

    if response.status_code == 200:
        data = response.json()
        return data['latestPrice'] # This is the latest price of the stock
    else:
        return None