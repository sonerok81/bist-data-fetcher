import os
import investpy
import yfinance as yf
import pandas as pd
from joblib import Memory

# Cache ayarı: aynı parametrelerle yapılan çağrıları diskten hızlıca döndürür
memory = Memory(".cache", verbose=0)

# Verilerin saklanacağı dizin
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

@memory.cache
def get_bist_tickers() -> list[str]:
    """Investpy ile Borsa İstanbul hisselerini çeker ve '.IS' uzantısını ekler."""
    lst = investpy.get_stocks_list(country='turkey')
    return [s + '.IS' for s in lst]

@memory.cache
def fetch_and_save_ohlcv(
    tickers: list[str] | None = None,
    period: str = "1y",
    interval: str = "1d"
) -> pd.DataFrame:
    """
    - tickers: Liste verilmezse tüm BIST hisseleri kullanılır.
    - period: '1d','1mo','1y' gibi periyot.
    - interval: '1d','1h','15m' vb.
    - Veriyi indirir ve data/bist_ohlcv.parquet dosyasına kaydeder.
    - Kaydedilmiş dosya varsa doğrudan onu yükler.
    """
    path = os.path.join(DATA_DIR, 'bist_ohlcv.parquet')
    if os.path.exists(path):
        df = pd.read_parquet(path)
    else:
        if tickers is None:
            tickers = get_bist_tickers()
        df = yf.download(
            tickers,
            period=period,
            interval=interval,
            group_by="ticker",
            threads=True
        )
        # Parquet formatında kaydet
        df.to_parquet(path)
    return df
