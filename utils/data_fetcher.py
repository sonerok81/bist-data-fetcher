# utils/data_fetcher.py

import os, time
import investpy
import yfinance as yf
import pandas as pd
from joblib import Memory

memory = Memory(".cache", verbose=0)
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(DATA_DIR, exist_ok=True)
CACHE_FILE = os.path.join(DATA_DIR, 'bist_ohlcv.parquet')

@memory.cache
def get_bist_tickers() -> list[str]:
    lst = investpy.get_stocks_list(country='turkey')
    return [s + '.IS' for s in lst]

def fetch_and_save_ohlcv(
    tickers: list[str]|None = None,
    period: str = "1y",
    interval: str = "1d",
    max_age_hours: int = 24
) -> pd.DataFrame:
    # Eğer dosya yoksa veya MAX_AGE'i aştıysa yeniden indir
    if os.path.exists(CACHE_FILE):
        age = (time.time() - os.path.getmtime(CACHE_FILE)) / 3600
        if age < max_age_hours:
            return pd.read_parquet(CACHE_FILE)
    if tickers is None:
        tickers = get_bist_tickers()
    df = yf.download(
        tickers,
        period=period,
        interval=interval,
        group_by="ticker",
        threads=True
    )
    df.to_parquet(CACHE_FILE)
    return df
