import numpy as np
from typing import List
from dataclasses import dataclass


@dataclass
class RSIResult:
    values: np.ndarray
    period: int


def calculate_rsi(prices: List[float], period: int = 14) -> RSIResult:
    """
    Wilder's RSI using exponential smoothing.

    Returns array of same length as prices — first `period` values are NaN.
    """
    arr = np.array(prices, dtype=float)
    delta = np.diff(arr)

    gains = np.where(delta > 0, delta, 0.0)
    losses = np.where(delta < 0, -delta, 0.0)

    rsi = np.full(len(arr), np.nan)

    # Seed with simple average
    avg_gain = gains[:period].mean()
    avg_loss = losses[:period].mean()

    for i in range(period, len(delta)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        rs = avg_gain / avg_loss if avg_loss > 0 else 1e9
        rsi[i + 1] = 100 - 100 / (1 + rs)

    return RSIResult(values=rsi, period=period)
