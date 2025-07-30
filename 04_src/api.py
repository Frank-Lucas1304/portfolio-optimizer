import requests
import pandas as pd 
class API:

    KEY = "wUvM2M29ZVxHDvK8IRp2P7iyrT8uhQG4"
    BASE_URL = "https://financialmodelingprep.com/stable/"
    
    # Might need to track number of API CALLS PER MINUTE
    
    def fetch(endpoint="", query="",verbose=False):
        url = f"{API.BASE_URL}{endpoint}?{query}&apikey={API.KEY}"
        if verbose:
            print(f"\trequest url:{url}")
        response = requests.get(url)
        json_response = response.json() 
        return pd.DataFrame(json_response)
           
    def fetch_sp500_constituent_info():
        df_constituent_full_info = API.fetch("sp500-constituent")
        df_constituent_full_info.set_index('symbol', inplace=True)
        df_constituent_light_info = df_constituent_full_info[['sector','subSector']] 
        return df_constituent_light_info

    # The "date" in the responses of fetch_ticker_key_metrics() and fetch_ticker_financial_ratios() represents the end date of the period the financial statement covers 
    def fetch_ticker_key_metrics(symbol,period="quarter"):
        endpoint = "key-metrics"
        query = f"symbol={symbol}&period={period}"
        df_key_metrics = API.fetch(endpoint,query)
        return API.set_index_and_sort(df_key_metrics)

    def fetch_ticker_financial_ratios(symbol,period="quarter"):
        endpoint = "ratios"
        query = f"symbol={symbol}&period={period}"
        df_financial_ratio = API.fetch(endpoint,query)
        return API.set_index_and_sort(df_financial_ratio)

    # For fetch price --> get the full list and then process in order to reduce the number of API calls
    def fetch_ticker_hist_price(symbol):
        endpoint = "historical-price-eod/full"
        query = f"symbol={symbol}"
        df_hist_price = API.fetch(endpoint,query)
        return API.set_index_and_sort(df_hist_price)
    
    def set_index_and_sort(df,index="date"):
        df.set_index('date', inplace=True)
        df.index = pd.to_datetime(df.index)
        df = df.sort_index(ascending=True)
        return df