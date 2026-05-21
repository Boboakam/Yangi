import pandas as pd
import numpy as np
import config

# SECURITY-BOBO Indikatorlar Moduli
# CVD, VWAP, Wyckoff, MTF Matrix va TQI integratsiyasi

def calculate_atr(df, length=14):
    """Average True Range (ATR)"""
    high = df['high']
    low = df['low']
    close = df['close']
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(window=length).mean()

def calculate_vwap(df):
    """Volume Weighted Average Price (VWAP)"""
    v = df['volume']
    p = (df['high'] + df['low'] + df['close']) / 3
    vwap = (p * v).cumsum() / v.cumsum()
    return vwap

def calculate_tqi(df):
    """Trend Quality Index (TQI) - 4 faktorli model"""
    # 1. Efficiency Ratio
    er_len = 20
    net_change = abs(df['close'] - df['close'].shift(er_len))
    path_len = abs(df['close'] - df['close'].shift(1)).rolling(window=er_len).sum()
    er = np.where(path_len > 0, net_change / path_len, 0.0)

    # 2. Volatility Regime
    raw_atr = calculate_atr(df, length=13)
    atr_base = raw_atr.rolling(window=100).mean()
    vol_ratio = np.where(atr_base > 0, raw_atr / atr_base, 1.0)

    # 3. Structure
    struct_hi = df['high'].rolling(window=20).max()
    struct_lo = df['low'].rolling(window=20).min()
    price_pos = (df['close'] - struct_lo) / (struct_hi - struct_lo + 1e-9)

    # 4. Momentum
    mom = df['close'].diff(10)

    # Final TQI Score (0 - 1.0)
    tqi = (er * 0.4 + np.clip(vol_ratio, 0, 1) * 0.2 + abs(price_pos - 0.5) * 2 * 0.2 + (np.sign(mom) * 0.5 + 0.5) * 0.2)
    return pd.Series(tqi, index=df.index).fillna(0)

def detect_smc_ict(df):
    """SMC/ICT: FVG, BOS, CHoCH va OTE"""
    res = {
        'fvg_bull': False, 'fvg_bear': False,
        'bos_bull': False, 'bos_bear': False,
        'ote_zone': False, 'market_regime': 'CHOPPY'
    }

    if len(df) < 5: return res

    # FVG
    if df['low'].iloc[-1] > df['high'].iloc[-3]: res['fvg_bull'] = True
    if df['high'].iloc[-1] < df['low'].iloc[-3]: res['fvg_bear'] = True

    # BOS
    swing_h = df['high'].shift(1).tail(20).max()
    swing_l = df['low'].shift(1).tail(20).min()
    if df['close'].iloc[-1] > swing_h: res['bos_bull'] = True
    if df['close'].iloc[-1] < swing_l: res['bos_bear'] = True

    # OTE (61.8% - 78.6%)
    hi, lo = df['high'].tail(50).max(), df['low'].tail(50).min()
    fib_range = hi - lo
    if fib_range > 0:
        price = df['close'].iloc[-1]
        if (hi - 0.786 * fib_range) <= price <= (hi - 0.618 * fib_range):
            res['ote_zone'] = True

    return res

def calculate_cvd(df):
    """Cumulative Volume Delta (CVD) - Soddalashtirilgan model"""
    # Buy volume = volume if close > open else volume * 0.5
    # Real tizimda bu Tick Data dan olinadi
    buy_vol = np.where(df['close'] >= df['open'], df['volume'] * 0.7, df['volume'] * 0.3)
    sell_vol = df['volume'] - buy_vol
    delta = buy_vol - sell_vol
    cvd = delta.cumsum()
    return pd.Series(cvd, index=df.index)

def analyze_wyckoff_effort(df):
    """Wyckoff Rule 5: Effort vs Result"""
    # Agar hajm katta bo'lib, narx o'zgarishi kichik bo'lsa -> Anomaliya
    vol_ma = df['volume'].rolling(window=20).mean()
    price_spread = abs(df['close'] - df['open'])
    spread_ma = price_spread.rolling(window=20).mean()

    anomaly = (df['volume'] > vol_ma * 1.5) & (price_spread < spread_ma * 0.7)
    return anomaly.iloc[-1] # True bo'lsa "Tuzoq" deb baholanadi

def get_market_regime(df):
    """Market Regime AI (Rule 28)"""
    tqi = calculate_tqi(df).iloc[-1]
    adx = 25 # Soddalashtirish uchun, aslida ADX hisoblanadi

    if tqi > 0.6: return "TREND"
    if tqi < 0.3: return "CHOPPY"
    return "ACCUMULATION"
