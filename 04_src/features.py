import pandas as pd
from .api import API
from .data import FolderStructure, CSV, Dir
class Signals:

    EXCLUDE_COLS = ['symbol','fiscalYear','period','reportedCurrency'] 

    
    def construct_features(symbol,period='quarter'):
        df_label = pd.DataFrame({'y':[]})
        df_all_info = Signals.growth_statements_info(symbol,period)
        df_stock = Signals.stock_insight(symbol)
        df_stock.index = pd.to_datetime(df_stock.index)

        df_all_info = df_all_info.merge(df_stock,on='date')
        df_label["y"] = df_all_info['ret_30d']
        df_label = df_label.shift(-1)
        df_all_info['y'] = df_label

        FolderStructure.write_ticker_csv(df_all_info,Dir.INTERIM,symbol,f"{symbol}.csv")

    def growth_statements_info(symbol,period='quarter',num_periods_compared=1):

        df_growth_info_raw = FolderStructure.read_raw_ticker_csv(symbol,CSV.RATIOS)
        df_metrics_raw = FolderStructure.read_raw_ticker_csv(symbol,CSV.KEY_METRIC)

        #df_growth_info_raw = API.fetch_ticker_financial_ratios(symbol,period)
        #df_metrics_raw = API.fetch_ticker_key_metrics(symbol,period) 
        df_growth_info_raw.merge(df_metrics_raw,on='date')
        df_growth_info = df_growth_info_raw[Signals.EXCLUDE_COLS]

        for gap in range(1,num_periods_compared+1):
            df_p_growth = df_growth_info_raw.drop(columns=Signals.EXCLUDE_COLS).pct_change(gap)
            new_columns_names = [name+"_"+str(gap)+"p" for name in df_p_growth.columns]
            df_p_growth.columns = new_columns_names
            df_growth_info.loc[:,df_p_growth.columns] = df_p_growth
        
        # replace end of period dates by business days since sometimes they are on weekends
        df_growth_info = df_growth_info.reset_index()
        df_growth_info['date'] = pd.to_datetime(df_growth_info['date'])
        df_growth_info['date']= df_growth_info['date'].apply(lambda d: d if d.weekday() < 5 else d - pd.offsets.BDay(1))

        df_growth_info.set_index('date',inplace=True)
  
        #FolderStructure.write_processed_ticker_csv(df_growth_info,symbol,CSV.GROWTH) TESTING
        return df_growth_info
    
    def stock_insight(symbol): # Determine Analysis Period
        #df_hist_raw = API.fetch_ticker_hist_price(symbol)
        df_hist_raw = FolderStructure.read_raw_ticker_csv(symbol,CSV.STOCK_HIST)

        # For dataframe subtractions collumns must have same names. This is not the case for series
        closing_price = df_hist_raw['close']
        low_price = df_hist_raw['low']
        high_price = df_hist_raw['high']
        volume = df_hist_raw["volume"]

        # Return
        ret_1d = closing_price.pct_change()
        ret_2d = closing_price.pct_change(2)
        ret_5d = closing_price.pct_change(5)
        ret_10d = closing_price.pct_change(10)
        ret_20d = closing_price.pct_change(20)
        ret_30d = closing_price.pct_change(30)

        # Volatility
        vol_5d = closing_price.pct_change().shift(1).rolling(window=5).std()
        vol_10d = closing_price.pct_change().shift(1).rolling(window=10).std()

        # Momentum
        momentum_10d = closing_price - closing_price.shift(10)

        # MFV
        mfm = ((closing_price-low_price) - (high_price-closing_price))/(high_price-low_price)
        mfv = mfm * volume
        ad_line = mfv.cumsum()
        AD_momentum_5d = ad_line.pct_change(5)
        AD_momentum_10d = ad_line.pct_change(10)
        AD_momentum_20d = ad_line.pct_change(20)

        # SMA Ratio
        sma_10 = closing_price.shift(1).rolling(window=10).mean()
        sma_50 = closing_price.shift(1).rolling(window=50).mean()
        sma_ratio = sma_10/sma_50

        # Z-score (20d)
        rolling_mean = closing_price.shift(1).rolling(window=20).mean()
        rolling_std = closing_price.shift(1).rolling(window=20).std()
        z_score_20d = (closing_price - rolling_mean)/rolling_std

        # RSI (14d)
        delta = closing_price.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)

        avg_gain = gain.shift(1).rolling(window=14).mean()
        avg_loss = loss.shift(1).rolling(window=14).mean()

        rs = avg_gain/avg_loss
        rsi_14 = 100 - (100 / (1 + rs))
        
        dataframes = [
        (ret_1d, 'ret_1d'),
        (ret_2d, 'ret_2d'),
        (ret_5d, 'ret_5d'),
        (ret_10d, 'ret_10d'),
        (ret_20d, 'ret_20d'),
        (ret_30d, 'ret_30d'),
        (vol_5d, 'vol_5d'),
        (vol_10d, 'vol_10d'),
        (momentum_10d, 'momentum_10d'),
        (sma_ratio, 'sma_ratio_10_50'),
        (z_score_20d, 'zscore_20d'),
        (rsi_14, 'rsi_14'),
        (volume,'volume'),
        (AD_momentum_5d,'AD_momentum_5d'),
        (AD_momentum_10d,'AD_momentum_10d'),
        (AD_momentum_20d,'AD_momentum_20d')
        ]


        for column, name in dataframes:
            column.name = name

        df_stock_insight = pd.concat(
            [column for column, _ in dataframes],
            axis=1
        )
        
        #FolderStructure.write_processed_ticker_csv(df_stock_insight,symbol,CSV.STOCK_HIST) # TESTING
        return df_stock_insight

    def process_data():
        df = FolderStructure.read_external_csv(CSV.SP500)
        print("Processing data...")
        for index, row in df.iterrows():
            print(f"\t[{index}/500] - {row['symbol']}" )
            Signals.construct_features(row['symbol'],period='anual')
            break # REMOVE
    
    # NEED TO CONSIDER HOW TO SEPERATE THE DATA