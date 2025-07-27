from pathlib import Path
import pandas as pd
from .api import API

class Dir:

    ROOT = Path.cwd() 

    DATA = ROOT / "data"
    MODEL = ROOT / 'model'

    RAW = DATA / 'raw'
    INTERIM = DATA /  'interim'
    PROCESSED = DATA / 'processed'
    EXTERNAL = DATA / 'external'


# file names
class CSV:
    SP500 = 'sp500_constituent.csv'
    KEY_METRIC = 'key_metrics.csv'
    RATIOS = 'ratios.csv'
    STOCK_HIST = 'stock_hist.csv'
    GROWTH = 'growth.csv' # basically merge of key_metrics and ratios csv

class FolderStructure:

    def create():
        Dir.ROOT.mkdir(parents=True, exist_ok=True)
        #FolderStructure.download_sp500_constituent_info() # need to be added later
        
        Dir.RAW.mkdir(parents=True, exist_ok=True)
        Dir.EXTERNAL.mkdir(parents=True, exist_ok=True)
        Dir.PROCESSED.mkdir(parents=True, exist_ok=True)
        Dir.INTERIM.mkdir(parents=True, exist_ok=True)

        Dir.MODEL.mkdir(parents=True, exist_ok=True)

    def load_data():
        df = FolderStructure.read_external_csv(CSV.SP500)
        print("Loading data...")
        for index, row in df.iterrows():
            print(f"\t[{index}/500] - {row['symbol']}" )
            FolderStructure.download_ticker_raw_data(row['symbol'], 'anual', add=row['sector'])
            break


    
    def read_ticker_csv(stage_dir, symbol, csv_name):
        target_dir = stage_dir / 'tickers' / symbol
        target_dir.mkdir(parents=True, exist_ok=True)
        df = pd.read_csv(target_dir / csv_name,index_col='date')
        return df

    
    def write_ticker_csv(df, stage_dir, symbol, csv_name):
        target_dir = stage_dir / 'tickers' / symbol
        target_dir.mkdir(parents=True, exist_ok=True)
        df.to_csv(target_dir / csv_name)

    
    def read_raw_ticker_csv(symbol, csv_name):
        return FolderStructure.read_ticker_csv(Dir.RAW, symbol, csv_name)

    
    def read_interim_ticker_csv(symbol, csv_name):
        return FolderStructure.read_ticker_csv(Dir.PROCESSED, symbol, csv_name)

    
    def read_external_csv(csv_name):
        target_dir = Dir.EXTERNAL
        target_dir.mkdir(parents=True, exist_ok=True)
        df = pd.read_csv(target_dir / csv_name)
        return df


    
    def write_processed_ticker_csv(df, symbol, csv_name):
        FolderStructure.write_ticker_csv(df, Dir.PROCESSED, symbol, csv_name)

    
    def download_sp500_constituent_info():
        df = API.fetch_sp500_constituent_info()
        df.to_csv(Dir.EXTERNAL / CSV.SP500)

    
    def download_ticker_raw_data(symbol, period="quarter", add=""):
        parent = Dir.RAW / 'tickers' / symbol
        parent.mkdir(parents=True, exist_ok=True)
        df_stock_hist = API.fetch_ticker_hist_price(symbol)
        df_stock_hist.to_csv(parent / CSV.STOCK_HIST)

        df_key_metrics = API.fetch_ticker_key_metrics(symbol, period)
        df_key_metrics.to_csv(parent / CSV.KEY_METRIC)

        df_ratios = API.fetch_ticker_financial_ratios(symbol, period)
        df_ratios.to_csv(parent / CSV.RATIOS)

    
    def process_ticker_data(symbol, period="quarter"):
        raw_dir = Dir.RAW / 'tickers' / symbol
        raw_dir.mkdir(parents=True, exist_ok=True)

        train_dir = Dir.PROCESSED / 'train'
        train_dir.mkdir(parents=True, exist_ok=True)

        test_dir = Dir.PROCESSED / 'test'
        test_dir.mkdir(parents=True, exist_ok=True)
