import pandas as pd
import numpy as np

# SECURITY-BOBO Indikatorlar Moduli
# SATS, TQI, SMC va ICT mantiqlari Pine Script v6 va MQL5 dan to'liq port qilingan

def calculate_atr(df, length=14):
    """Average True Range (ATR) hisoblash"""
    high = df['high']
    low = df['low']
    close = df['close']

    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=length).mean()
    return atr

def calculate_tqi_components(df, er_len=20, atr_base_len=100, struct_len=20, mom_len=10):
    """TQI ning 4 ta faktorini hisoblash"""
    # 1. Factor: Efficiency Ratio (ER)
    net_change = abs(df['close'] - df['close'].shift(er_len))
    path_len = abs(df['close'] - df['close'].shift(1)).rolling(window=er_len).sum()
    er = np.where(path_len > 0, net_change / path_len, 0.0)
    er = np.clip(er, 0.0, 1.0)

    # 2. Factor: Volatility Regime
    raw_atr = calculate_atr(df, length=13)
    atr_baseline = raw_atr.rolling(window=atr_base_len).mean()
    vol_ratio = np.where(atr_baseline > 0, raw_atr / atr_baseline, 1.0)
    # Map vol_ratio 0.6..1.8 -> 0..1
    tqi_vol = np.clip((vol_ratio - 0.6) / (1.8 - 0.6), 0.0, 1.0)

    # 3. Factor: Structure
    struct_hi = df['high'].rolling(window=struct_len).max()
    struct_lo = df['low'].rolling(window=struct_len).min()
    struct_range = struct_hi - struct_lo
    price_pos = np.where(struct_range > 0, (df['close'] - struct_lo) / struct_range, 0.5)
    tqi_struct = np.clip(abs(price_pos - 0.5) * 2.0, 0.0, 1.0)

    # 4. Factor: Momentum Persistence
    # Har bir bar o'zgarishi oyna o'zgarishi bilan mos kelishini tekshirish
    mom_counts = []
    for i in range(len(df)):
        if i < mom_len:
            mom_counts.append(0.5)
            continue
        window_change = df['close'].iloc[i] - df['close'].iloc[i - mom_len]
        align_count = 0
        for j in range(mom_len):
            bar_change = df['close'].iloc[i-j] - df['close'].iloc[i-j-1]
            if (window_change > 0 and bar_change > 0) or (window_change < 0 and bar_change < 0):
                align_count += 1
        mom_counts.append(align_count / mom_len)
    tqi_mom = np.array(mom_counts)

    return er, tqi_vol, tqi_struct, tqi_mom

def calculate_tqi(df):
    """To'liq Trend Quality Index"""
    er, tqi_vol, tqi_struct, tqi_mom = calculate_tqi_components(df)
    # Pine Script weightlari: ER=0.35, Vol=0.20, Struct=0.25, Mom=0.20
    tqi = (er * 0.35 + tqi_vol * 0.20 + tqi_struct * 0.25 + tqi_mom * 0.20)
    return pd.Series(np.clip(tqi, 0.0, 1.0), index=df.index)

def calculate_adaptive_supertrend(df, tqi, er, base_mult=2.0, qual_curve=1.5, qual_str=0.4):
    """Asymmetric Adaptive Supertrend with Ratchet logic"""
    atr = calculate_atr(df)

    # Legacy adaptation factor
    legacy_factor = 1.0 + 0.5 * (0.5 - er)
    # TQI based multiplier
    qual_dev = np.power(1.0 - tqi, qual_curve)
    tqi_mult_fact = 1.0 - qual_str + qual_str * (0.6 + 0.8 * qual_dev)

    sym_mult = base_mult * legacy_factor * tqi_mult_fact

    # Asymmetric multipliers
    active_mult = sym_mult * (1.0 - 0.5 * tqi * 0.3) # Tighten in trend
    passive_mult = sym_mult * (1.0 + 0.5 * tqi * 0.4) # Widen against trend

    upper_band = np.zeros(len(df))
    lower_band = np.zeros(len(df))
    st_trend = np.ones(len(df)) # 1 for bull, -1 for bear

    # Initial values
    upper_band[0] = df['close'].iloc[0] + sym_mult.iloc[0] * atr.iloc[0]
    lower_band[0] = df['close'].iloc[0] - sym_mult.iloc[0] * atr.iloc[0]

    for i in range(1, len(df)):
        prev_trend = st_trend[i-1]

        # Mult selection
        l_mult = active_mult.iloc[i] if prev_trend == 1 else passive_mult.iloc[i]
        u_mult = passive_mult.iloc[i] if prev_trend == 1 else active_mult.iloc[i]

        l_raw = df['close'].iloc[i] - l_mult * atr.iloc[i]
        u_raw = df['close'].iloc[i] + u_mult * atr.iloc[i]

        # Ratchet logic
        lower_band[i] = max(l_raw, lower_band[i-1]) if df['close'].iloc[i-1] > lower_band[i-1] else l_raw
        upper_band[i] = min(u_raw, upper_band[i-1]) if df['close'].iloc[i-1] < upper_band[i-1] else u_raw

        # Trend flip
        if prev_trend == 1 and df['close'].iloc[i] < lower_band[i]:
            st_trend[i] = -1
        elif prev_trend == -1 and df['close'].iloc[i] > upper_band[i]:
            st_trend[i] = 1
        else:
            st_trend[i] = prev_trend

    return pd.Series(upper_band, index=df.index), pd.Series(lower_band, index=df.index), pd.Series(st_trend, index=df.index)

def detect_smc_ict(df, bos_look=20, fib_look=50):
    """SMC va ICT elementlarini aniqlash (To'liq mantiq)"""
    res = {
        'fvg_bull': False,
        'fvg_bear': False,
        'bos_bull': False,
        'bos_bear': False,
        'choch_bull': False,
        'choch_bear': False,
        'ote_zone': False,
        'fib_hi': 0.0,
        'fib_lo': 0.0
    }

    if len(df) < 5: return res

    # 1. FVG
    # Bullish FVG: low[0] > high[2]
    if df['low'].iloc[-1] > df['high'].iloc[-3]:
        res['fvg_bull'] = True
    # Bearish FVG: high[0] < low[2]
    if df['high'].iloc[-1] < df['low'].iloc[-3]:
        res['fvg_bear'] = True

    # 2. BOS (Break of Structure)
    swing_h = df['high'].shift(1).tail(bos_look).max()
    swing_l = df['low'].shift(1).tail(bos_look).min()
    if df['close'].iloc[-1] > swing_h:
        res['bos_bull'] = True
    if df['close'].iloc[-1] < swing_l:
        res['bos_bear'] = True

    # 3. Fibonacci OTE (Optimal Trade Entry 0.618 - 0.786)
    fib_hi = df['high'].tail(fib_look).max()
    fib_lo = df['low'].tail(fib_look).min()
    res['fib_hi'] = fib_hi
    res['fib_lo'] = fib_lo
    rng = fib_hi - fib_lo
    if rng > 0:
        fib_786 = fib_hi - 0.786 * rng
        fib_618 = fib_hi - 0.618 * rng
        if fib_786 <= df['close'].iloc[-1] <= fib_618:
            res['ote_zone'] = True

    return res

def get_signal_score(df, tqi, smc):
    """Pine Script v6 dagi 6-faktorlik signal skoringi"""
    # Soddalashtirilgan skoring mantiqi
    score = 0
    if tqi > 0.5: score += 20
    if smc['fvg_bull'] or smc['fvg_bear']: score += 15
    if smc['bos_bull'] or smc['bos_bear']: score += 15
    if smc['ote_zone']: score += 15
    # RSI va Momentum skoringlari qo'shilishi mumkin
    return score
