"""
EMA + RSI + Volume strategy backtest on BTC-USD daily data.

Walk-forward split:
  In-sample  (IS) : 2020-01-01 – 2022-12-31
  Out-of-sample (OOS): 2023-01-01 – 2024-12-31

Run:
    pip install yfinance
    python examples/ema_backtest.py
"""
import numpy as np
import pandas as pd

# ── data ─────────────────────────────────────────────────────────────────────

def load_data(ticker: str = "BTC-USD",
              start: str = "2020-01-01",
              end:   str = "2024-12-31") -> pd.DataFrame:
    try:
        import yfinance as yf
        df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
        df.columns = [c.lower() for c in df.columns]
        df = df[["open", "high", "low", "close", "volume"]].dropna()
        print(f"Downloaded {len(df)} bars for {ticker} from Yahoo Finance")
        return df
    except Exception as e:
        print(f"yfinance failed ({e}), using synthetic data")
        return _synthetic_btc(start, end)


def _synthetic_btc(start: str, end: str) -> pd.DataFrame:
    """Realistic BTC-like synthetic price series with trend + noise."""
    idx = pd.date_range(start, end, freq="B")
    n   = len(idx)
    np.random.seed(42)
    log_returns = np.random.normal(0.001, 0.025, n)
    price = 9000 * np.exp(np.cumsum(log_returns))
    df = pd.DataFrame({
        "open":   price * (1 - np.abs(np.random.normal(0, 0.003, n))),
        "high":   price * (1 + np.abs(np.random.normal(0, 0.012, n))),
        "low":    price * (1 - np.abs(np.random.normal(0, 0.012, n))),
        "close":  price,
        "volume": np.random.lognormal(15, 0.5, n),
    }, index=idx)
    print(f"Generated {len(df)} synthetic bars")
    return df

# ── indicators ───────────────────────────────────────────────────────────────

def ema(series: np.ndarray, period: int) -> np.ndarray:
    alpha = 2 / (period + 1)
    out = np.empty_like(series)
    out[0] = series[0]
    for i in range(1, len(series)):
        out[i] = alpha * series[i] + (1 - alpha) * out[i - 1]
    return out


def rsi(series: np.ndarray, period: int = 14) -> np.ndarray:
    delta = np.diff(series)
    gains  = np.where(delta > 0, delta, 0.0)
    losses = np.where(delta < 0, -delta, 0.0)
    result = np.full(len(series), np.nan)
    avg_g = gains[:period].mean()
    avg_l = losses[:period].mean()
    for i in range(period, len(delta)):
        avg_g = (avg_g * (period - 1) + gains[i]) / period
        avg_l = (avg_l * (period - 1) + losses[i]) / period
        rs = avg_g / avg_l if avg_l > 0 else 1e9
        result[i + 1] = 100 - 100 / (1 + rs)
    return result


def atr(high: np.ndarray, low: np.ndarray, close: np.ndarray,
        period: int = 14) -> np.ndarray:
    tr = np.maximum(
        high[1:] - low[1:],
        np.maximum(np.abs(high[1:] - close[:-1]),
                   np.abs(low[1:] - close[:-1])),
    )
    tr = np.concatenate([[tr[0]], tr])
    result = np.empty_like(close)
    result[:period] = tr[:period].mean()
    for i in range(period, len(close)):
        result[i] = (result[i - 1] * (period - 1) + tr[i]) / period
    return result

# ── backtest engine ───────────────────────────────────────────────────────────

def run_backtest(df: pd.DataFrame,
                 fast: int = 10,
                 slow: int = 30,
                 rsi_period: int = 14,
                 rsi_ob: float = 65,
                 rsi_os: float = 35,
                 vol_mult: float = 1.5,
                 atr_stop: float = 2.0,
                 commission: float = 0.001,
                 capital: float = 10_000.0) -> dict:
    """
    Vectorised walk-through of the strategy.

    Signal logic:
      Long  : fast EMA crosses above slow EMA  + RSI < rsi_ob + volume > vol_mult × MA20
      Short : fast EMA crosses below slow EMA  + RSI > rsi_os + volume > vol_mult × MA20
      Exit  : opposite crossover  OR  price moves 2×ATR against entry
    """
    closes  = df["close"].values.astype(float)
    highs   = df["high"].values.astype(float)
    lows    = df["low"].values.astype(float)
    volumes = df["volume"].values.astype(float)

    fast_ema = ema(closes, fast)
    slow_ema = ema(closes, slow)
    rsi_vals = rsi(closes, rsi_period)
    atr_vals = atr(highs, lows, closes, 14)
    vol_ma   = pd.Series(volumes).rolling(20).mean().values

    equity = np.full(len(closes), capital)
    position   = 0          # +1 long, -1 short, 0 flat
    entry_price = 0.0
    trades: list = []

    warmup = max(slow, rsi_period, 20) + 2

    for i in range(warmup, len(closes)):
        price = closes[i]
        cross_now  = fast_ema[i]     - slow_ema[i]
        cross_prev = fast_ema[i - 1] - slow_ema[i - 1]
        curr_rsi   = rsi_vals[i]
        vol_ok     = volumes[i] > vol_ma[i] * vol_mult if not np.isnan(vol_ma[i]) else False

        # ── exit conditions ───────────────────────────────────────────────
        if position != 0:
            stop_dist = atr_vals[i] * atr_stop
            hit_stop = (
                (position ==  1 and price < entry_price - stop_dist) or
                (position == -1 and price > entry_price + stop_dist)
            )
            reverse = (
                (position ==  1 and cross_prev >= 0 and cross_now < 0) or
                (position == -1 and cross_prev <= 0 and cross_now > 0)
            )
            if hit_stop or reverse:
                pnl_pct = position * (price / entry_price - 1) - commission
                equity[i] = equity[i - 1] * (1 + pnl_pct)
                trades.append({"entry": entry_price, "exit": price,
                                "side": position, "pnl_pct": pnl_pct * 100})
                position = 0
            else:
                equity[i] = equity[i - 1]

        # ── entry conditions ──────────────────────────────────────────────
        if position == 0:
            if (cross_prev <= 0 and cross_now > 0
                    and not np.isnan(curr_rsi)
                    and curr_rsi < rsi_ob
                    and vol_ok):
                position = 1
                entry_price = price * (1 + commission)
                equity[i] = equity[i - 1]

            elif (cross_prev >= 0 and cross_now < 0
                    and not np.isnan(curr_rsi)
                    and curr_rsi > rsi_os
                    and vol_ok):
                position = -1
                entry_price = price * (1 - commission)
                equity[i] = equity[i - 1]
            else:
                equity[i] = equity[i - 1]

    eq = pd.Series(equity, index=df.index)
    ret = eq.pct_change().dropna()

    sharpe  = (ret.mean() / ret.std() * np.sqrt(252)) if ret.std() > 0 else 0.0
    total_r = (eq.iloc[-1] / eq.iloc[0] - 1) * 100
    max_dd  = ((eq - eq.cummax()) / eq.cummax()).min() * 100
    wr      = sum(1 for t in trades if t["pnl_pct"] > 0) / len(trades) * 100 if trades else 0

    return {
        "equity":       eq,
        "trades":       trades,
        "total_return": round(total_r, 2),
        "sharpe":       round(sharpe, 3),
        "max_dd":       round(max_dd, 2),
        "win_rate":     round(wr, 1),
        "n_trades":     len(trades),
        "avg_trade":    round(np.mean([t["pnl_pct"] for t in trades]), 3) if trades else 0,
    }

# ── reporting ─────────────────────────────────────────────────────────────────

def print_results(label: str, res: dict):
    print(f"\n{'─'*40}")
    print(f" {label}")
    print(f"{'─'*40}")
    print(f"  Total return : {res['total_return']:+.1f}%")
    print(f"  Sharpe ratio : {res['sharpe']:.3f}")
    print(f"  Max drawdown : {res['max_dd']:.1f}%")
    print(f"  Win rate     : {res['win_rate']:.1f}%")
    print(f"  Total trades : {res['n_trades']}")
    print(f"  Avg trade    : {res['avg_trade']:+.3f}%")


def ascii_equity(equity: pd.Series, width: int = 60, height: int = 12):
    vals = equity.values
    mn, mx = vals.min(), vals.max()
    norm = ((vals - mn) / (mx - mn) * (height - 1)).astype(int)
    step = max(1, len(vals) // width)
    sampled = norm[::step][:width]
    print(f"\n  Equity curve  ({equity.index[0].date()} → {equity.index[-1].date()})")
    print(f"  ${mx:,.0f} ┐")
    for row in range(height - 1, -1, -1):
        line = "".join("█" if v >= row else " " for v in sampled)
        print(f"         │{line}")
    print(f"  ${mn:,.0f} └" + "─" * width)


# ── main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    FAST, SLOW = 10, 30
    PARAMS = dict(fast=FAST, slow=SLOW, rsi_period=14,
                  rsi_ob=65, rsi_os=35, vol_mult=1.5,
                  atr_stop=2.0, commission=0.001)

    df = load_data("BTC-USD", "2020-01-01", "2024-12-31")

    IS  = df["2020-01-01":"2022-12-31"]
    OOS = df["2023-01-01":"2024-12-31"]

    print(f"\n  Strategy : EMA({FAST},{SLOW}) + RSI(14) filter + Volume(1.5×) confirmation")
    print(f"  Asset    : BTC-USD daily")
    print(f"  Costs    : 0.1% per trade (commission)")

    is_res  = run_backtest(IS,  **PARAMS)
    oos_res = run_backtest(OOS, **PARAMS)

    print_results("IN-SAMPLE  (2020–2022)", is_res)
    ascii_equity(is_res["equity"])

    print_results("OUT-OF-SAMPLE  (2023–2024)", oos_res)
    ascii_equity(oos_res["equity"])

    print(f"\n{'═'*40}")
    print("  NOTE: This is a demonstration of backtesting")
    print("  methodology. EMA crossover is a textbook")
    print("  strategy included to show the full pipeline.")
    print(f"{'═'*40}\n")
