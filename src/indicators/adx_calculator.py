import numpy as np
from typing import List
from dataclasses import dataclass


@dataclass
class ADXResult:
    adx: np.ndarray    # Average Directional Index (trend strength 0-100)
    plus_di: np.ndarray   # +DI (bullish directional movement)
    minus_di: np.ndarray  # -DI (bearish directional movement)
    period: int


def calculate_adx(high: List[float], low: List[float],
                  close: List[float], period: int = 14) -> ADXResult:
    """
    Wilder's ADX — measures trend strength regardless of direction.

    ADX > 25 : strong trend (tradeable)
    ADX < 20 : weak trend / sideways (avoid)
    ADX > 50 : very strong trend

    +DI > -DI : bullish pressure
    -DI > +DI : bearish pressure
    """
    h = np.array(high,  dtype=float)
    l = np.array(low,   dtype=float)
    c = np.array(close, dtype=float)
    n = len(c)

    plus_dm  = np.zeros(n)
    minus_dm = np.zeros(n)
    tr       = np.zeros(n)

    for i in range(1, n):
        up   = h[i] - h[i - 1]
        down = l[i - 1] - l[i]

        plus_dm[i]  = up   if (up > down and up > 0)   else 0.0
        minus_dm[i] = down if (down > up and down > 0) else 0.0

        tr[i] = max(h[i] - l[i],
                    abs(h[i] - c[i - 1]),
                    abs(l[i] - c[i - 1]))

    # Wilder smoothing
    def wilder_smooth(arr: np.ndarray, p: int) -> np.ndarray:
        out = np.zeros(n)
        out[p] = arr[1:p + 1].sum()
        for i in range(p + 1, n):
            out[i] = out[i - 1] - out[i - 1] / p + arr[i]
        return out

    atr_s    = wilder_smooth(tr,       period)
    plus_s   = wilder_smooth(plus_dm,  period)
    minus_s  = wilder_smooth(minus_dm, period)

    plus_di  = np.where(atr_s > 0, 100 * plus_s  / atr_s, 0.0)
    minus_di = np.where(atr_s > 0, 100 * minus_s / atr_s, 0.0)

    dx = np.where(
        (plus_di + minus_di) > 0,
        100 * np.abs(plus_di - minus_di) / (plus_di + minus_di),
        0.0,
    )

    adx = np.zeros(n)
    start = period * 2
    if start < n:
        adx[start] = dx[period:start + 1].mean()
        for i in range(start + 1, n):
            adx[i] = (adx[i - 1] * (period - 1) + dx[i]) / period

    return ADXResult(adx=adx, plus_di=plus_di, minus_di=minus_di, period=period)
