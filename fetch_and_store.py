# fetch_and_store.py

from utils.data_fetcher import fetch_and_save_ohlcv

if __name__ == "__main__":
    df = fetch_and_save_ohlcv(period="1y", interval="1d")
    print("Veri kaydedildi: data/bist_ohlcv.parquet")
    print(df.columns.levels[0].tolist(), "hisse bulundu.")
