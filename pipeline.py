# pipeline.py
import pandas as pd
import numpy as np
from arch import arch_model
from utils.data_fetcher import fetch_and_save_ohlcv

# ==== Thresholds: kolayca ayarlanabilir ====
SHARPE_THRESHOLD = 0.3
SORTINO_THRESHOLD = 0.8
ATR_MIN = 0.001   # %0.1
ATR_MAX = 0.10    # %10
VOLUME_THRESHOLD = 1000000  # Minimum günlük işlem hacmi
PRICE_THRESHOLD = 1.0  # Minimum fiyat

def calculate_macd(close, fast=12, slow=26, signal=9):
    """MACD hesaplama"""
    exp1 = close.ewm(span=fast, adjust=False).mean()
    exp2 = close.ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd, signal_line

def calculate_bollinger_bands(close, window=20, num_std=2):
    """Bollinger Bands hesaplama"""
    middle_band = close.rolling(window=window).mean()
    std = close.rolling(window=window).std()
    upper_band = middle_band + (std * num_std)
    lower_band = middle_band - (std * num_std)
    return middle_band, upper_band, lower_band

# 1) Veri yükleme: Son 500 iş günü
def load_raw_data() -> pd.DataFrame:
    df = fetch_and_save_ohlcv(period="2y", interval="1d")
    df.index = pd.to_datetime(df.index)
    return df.tail(500)

# 2) RSI hesaplama
def compute_rsi(close: pd.DataFrame, length: int = 14) -> pd.DataFrame:
    delta = close.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    ema_up = up.ewm(com=length-1, adjust=False).mean()
    ema_down = down.ewm(com=length-1, adjust=False).mean()
    rs = ema_up / ema_down
    return 100 - (100 / (1 + rs))

# 3) ATR hesaplama (her hisse için)
def compute_atr(high: pd.DataFrame, low: pd.DataFrame, close: pd.DataFrame, length: int = 14) -> pd.DataFrame:
    atr_dict = {}
    for sym in close.columns:
        h = high[sym]
        l = low[sym]
        c = close[sym]
        prev = c.shift(1)
        tr1 = h - l
        tr2 = (h - prev).abs()
        tr3 = (l - prev).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr_dict[sym] = tr.ewm(com=length-1, adjust=False).mean()
    return pd.DataFrame(atr_dict)

# 4) Getiri istatistikleri
def compute_return_stats(close: pd.DataFrame) -> pd.DataFrame:
    rets = close.pct_change(fill_method=None)
    mu = rets.mean()
    sigma = rets.std()
    sharpe = mu / sigma * np.sqrt(252)
    down = rets[rets < 0]
    sortino = mu / down.std() * np.sqrt(252)
    stats = pd.DataFrame({'Sharpe': sharpe, 'Sortino': sortino})
    print("Sharpe/Sortino dağılımı:")
    print(stats.describe())
    return stats

# 5) GARCH pozisyon ağırlığı
def compute_garch_weights(close: pd.DataFrame, target_vol: float = 0.15) -> pd.Series:
    rets = close.pct_change(fill_method=None) * 100
    weights = {}
    for sym in close.columns:
        series = rets[sym].dropna()
        try:
            am = arch_model(series, vol='Garch', p=1, q=1).fit(disp='off')
            fvar = am.forecast(horizon=1).variance.iloc[-1, 0] / 10000
            weights[sym] = target_vol / np.sqrt(fvar * 252)
        except:
            weights[sym] = 0.0
    return pd.Series(weights)

# 6) Teknik sinyaller
def compute_tech_signals(close: pd.DataFrame, vol: pd.DataFrame) -> pd.Series:
    rsi = compute_rsi(close)
    vol_ma = vol.rolling(20).mean()
    mom3m = close.pct_change(periods=63, fill_method=None)
    
    # MACD hesaplama
    macd_dict = {}
    for sym in close.columns:
        macd, _ = calculate_macd(close[sym])
        macd_dict[sym] = macd.iloc[-1]
    macd = pd.Series(macd_dict)
    
    # Bollinger Bands
    bb_dict = {}
    for sym in close.columns:
        _, upper, _ = calculate_bollinger_bands(close[sym])
        bb_dict[sym] = close[sym].iloc[-1] > upper.iloc[-1]
    bb = pd.Series(bb_dict)
    
    # Fiyat ve hacim filtreleri
    price_filter = close.iloc[-1] >= PRICE_THRESHOLD
    volume_filter = vol.iloc[-1] >= VOLUME_THRESHOLD
    
    cond = (
        (mom3m > 0) &
        (rsi > 30) & (rsi < 90) &
        (vol > 0.8 * vol_ma) &
        (macd > 0) &    # MACD pozitif
        bb &            # Fiyat BB üst bandının üstünde
        price_filter &  # Minimum fiyat kontrolü
        volume_filter   # Minimum hacim kontrolü
    )
    
    mask = cond.iloc[-1]
    print(f"Teknik sinyaller hesaplandı: {mask.sum()}/{len(mask)} hisse")
    return mask

# 7) Ana pipeline fonksiyonu
def run_pipeline() -> pd.DataFrame:
    raw = load_raw_data()
    close = raw.xs('Close', axis=1, level=1)
    high = raw.xs('High', axis=1, level=1)
    low = raw.xs('Low', axis=1, level=1)
    vol = raw.xs('Volume', axis=1, level=1)

    stats = compute_return_stats(close)
    filtered1 = stats[(stats.Sharpe >= SHARPE_THRESHOLD) & (stats.Sortino >= SORTINO_THRESHOLD)].index

    atr_df = compute_atr(high, low, close)
    atr_pct = atr_df.div(close)
    latest_atr = atr_pct.iloc[-1]
    print("ATR yüzdesi dağılımı:")
    print(latest_atr.describe())
    filtered2 = latest_atr[(latest_atr >= ATR_MIN) & (latest_atr <= ATR_MAX)].index

    universe = set(filtered1) & set(filtered2)
    if not universe:
        top10 = stats.sort_values('Sharpe', ascending=False).head(10).index
        universe = set(top10)
        print(f"Fallback: En iyi 10 Sharpe hisse: {list(universe)}")

    tech_mask = compute_tech_signals(close, vol)
    final = sorted([s for s in universe if tech_mask.get(s, False)])

    if not final:
        return pd.DataFrame(columns=['Ticker','Sharpe','Sortino','ATR%','Weight'])

    weights = compute_garch_weights(close[final])
    df_final = pd.DataFrame({
        'Ticker': final,
        'Sharpe': stats.Sharpe.loc[final],
        'Sortino': stats.Sortino.loc[final],
        'ATR%': latest_atr.loc[final],
        'Weight': weights.loc[final]
    }).reset_index(drop=True)
    
    # Ağırlıkları normalize et
    df_final['Weight'] = df_final['Weight'] / df_final['Weight'].sum()
    
    return df_final

# 8) Manuel çalıştırma
if __name__ == '__main__':
    df = run_pipeline()
    if df.empty:
        print("Hiç hisse kriterleri karşılamadı.")
    else:
        print("Tüm taranan hisseler:")
        print(df.to_string(index=False))
