"""
EMA crossover + RSI + ADX/SMA200 market-regime backtest on BTC-USD daily.

Strategy (long-only):
  Entry : EMA(10) crosses above EMA(30)
          AND RSI(14) < 65  (not overbought)
          AND ADX(14) > 20  (trending market)
          AND price > SMA(200)  (macro bull regime)
  Exit  : EMA bearish cross OR 2x ATR stop-loss

Walk-forward split:
  In-sample  (IS) : 2020-01-01 - 2022-12-31
  Out-of-sample (OOS): 2023-01-01 - 2024-12-31

Run:
    pip install yfinance
    python examples/ema_backtest.py
"""
import os
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", category=RuntimeWarning)

# ── data ─────────────────────────────────────────────────────────────────────

def load_data(ticker: str = "BTC-USD",
              start: str = "2020-01-01",
              end:   str = "2024-12-31") -> pd.DataFrame:
    try:
        import yfinance as yf
        df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
        # yfinance >= 0.2.x returns MultiIndex columns — flatten them
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0].lower() for c in df.columns]
        else:
            df.columns = [c.lower() for c in df.columns]
        df = df[["open", "high", "low", "close", "volume"]].dropna()
        if df.empty:
            raise ValueError("Empty dataframe returned")
        print(f"Downloaded {len(df)} bars for {ticker} from Yahoo Finance")
        return df
    except Exception as e:
        csv_path = "data/btc_daily.csv"
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path, index_col="date", parse_dates=True)
            df = df.loc[start:end]
            print(f"Loaded {len(df)} bars from {csv_path}")
            return df
        print(f"yfinance unavailable ({e}), using synthetic data")
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

def sma(series: np.ndarray, period: int) -> np.ndarray:
    out = np.full(len(series), np.nan)
    for i in range(period - 1, len(series)):
        out[i] = series[i - period + 1:i + 1].mean()
    return out


def calc_adx(high: np.ndarray, low: np.ndarray,
             close: np.ndarray, period: int = 14) -> np.ndarray:
    n = len(close)
    plus_dm = np.zeros(n)
    minus_dm = np.zeros(n)
    tr = np.zeros(n)
    for i in range(1, n):
        up   = high[i]  - high[i - 1]
        down = low[i - 1] - low[i]
        plus_dm[i]  = up   if (up > down   and up > 0)   else 0.0
        minus_dm[i] = down if (down > up   and down > 0) else 0.0
        tr[i] = max(high[i] - low[i],
                    abs(high[i]  - close[i - 1]),
                    abs(low[i]   - close[i - 1]))

    def ws(arr):
        out = np.zeros(n)
        out[period] = arr[1:period + 1].sum()
        for i in range(period + 1, n):
            out[i] = out[i-1] - out[i-1] / period + arr[i]
        return out

    atr_s = ws(tr); pd_s = ws(plus_dm); md_s = ws(minus_dm)
    pdi = np.where(atr_s > 0, 100 * pd_s / atr_s, 0.0)
    mdi = np.where(atr_s > 0, 100 * md_s / atr_s, 0.0)
    dx  = np.where((pdi + mdi) > 0, 100 * np.abs(pdi - mdi) / (pdi + mdi), 0.0)

    adx = np.zeros(n)
    start = period * 2
    if start < n:
        adx[start] = dx[period:start + 1].mean()
        for i in range(start + 1, n):
            adx[i] = (adx[i-1] * (period - 1) + dx[i]) / period
    return adx


def run_backtest(df: pd.DataFrame,
                 fast: int = 10,
                 slow: int = 30,
                 rsi_period: int = 14,
                 rsi_ob: float = 65,
                 rsi_os: float = 35,
                 atr_stop: float = 2.0,
                 adx_period: int = 14,
                 adx_threshold: float = 20.0,
                 sma_trend: int = 200,
                 commission: float = 0.001,
                 capital: float = 10_000.0) -> dict:
    """
    Long-only, bull-regime filter:
      1. EMA(fast) crosses above EMA(slow)  — momentum signal
      2. RSI < rsi_ob                        — not already overbought
      3. ADX > adx_threshold                 — trending, not choppy
      4. Price > SMA(sma_trend)              — macro bull regime

    Exit: EMA bearish crossover OR ATR(2x) stop-loss
    """
    closes = df["close"].values.astype(float)
    highs  = df["high"].values.astype(float)
    lows   = df["low"].values.astype(float)

    fast_ema = ema(closes, fast)
    slow_ema = ema(closes, slow)
    rsi_vals = rsi(closes, rsi_period)
    atr_vals = atr(highs, lows, closes, 14)
    adx_vals = calc_adx(highs, lows, closes, adx_period)
    sma200   = sma(closes, sma_trend)

    cur_capital = capital
    equity      = np.full(len(closes), capital)
    position    = 0
    entry_price = 0.0
    entry_bar   = 0
    trades: list = []

    warmup = max(slow, rsi_period, adx_period * 2, sma_trend) + 2

    for i in range(warmup, len(closes)):
        price      = closes[i]
        cross_now  = fast_ema[i]     - slow_ema[i]
        cross_prev = fast_ema[i - 1] - slow_ema[i - 1]
        curr_rsi   = rsi_vals[i]
        curr_adx   = adx_vals[i]
        curr_sma   = sma200[i]
        trend_ok  = curr_adx > adx_threshold
        above_sma = price > curr_sma if not np.isnan(curr_sma) else False

        # ── exit ─────────────────────────────────────────────────────────
        if position == 1:
            stop_dist = atr_vals[i] * atr_stop
            hit_stop = price < entry_price - stop_dist
            reverse  = cross_prev >= 0 and cross_now < 0
            if hit_stop or reverse:
                pnl_pct     = (price / entry_price - 1) - commission
                cur_capital *= (1 + pnl_pct)
                trades.append({
                    "entry":      entry_price,
                    "exit":       price,
                    "side":       1,
                    "pnl_pct":    pnl_pct * 100,
                    "entry_date": df.index[entry_bar],
                    "exit_date":  df.index[i],
                })
                position = 0

        # ── entry ─────────────────────────────────────────────────────────
        if position == 0:
            long_signal = (cross_prev <= 0 and cross_now > 0
                           and not np.isnan(curr_rsi)
                           and curr_rsi < rsi_ob
                           and trend_ok and above_sma)
            if long_signal:
                position    = 1
                entry_price = price * (1 + commission)
                entry_bar   = i

        equity[i] = cur_capital

    eq = pd.Series(equity, index=df.index)
    return {"equity": eq, "trades": trades}


def period_metrics(eq: pd.Series, trades: list) -> dict:
    """Compute performance metrics for a (sub-)period equity curve."""
    ret     = eq.pct_change().dropna()
    total_r = (eq.iloc[-1] / eq.iloc[0] - 1) * 100
    sharpe  = (ret.mean() / ret.std() * np.sqrt(252)) if ret.std() > 0 else 0.0
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
    print(f"\n" + "-"*40)
    print(f" {label}")
    print("-"*40)
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
    print(f"\n  Equity curve  ({equity.index[0].date()} to {equity.index[-1].date()})")
    print(f"  ${mx:,.0f} |")
    for row in range(height - 1, -1, -1):
        line = "".join("#" if v >= row else " " for v in sampled)
        print(f"         |{line}")
    print(f"  ${mn:,.0f} +" + "-" * width)


# ── main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    FAST, SLOW = 10, 30
    PARAMS = dict(fast=FAST, slow=SLOW, rsi_period=14,
                  rsi_ob=65, rsi_os=35,
                  atr_stop=2.0, adx_threshold=20.0, sma_trend=200,
                  commission=0.001)

    df = load_data("BTC-USD", "2020-01-01", "2024-12-31")

    print(f"\n  Strategy : EMA({FAST},{SLOW}) + RSI(14) + ADX>20 + SMA200 bull-regime filter")
    print(f"  Asset    : BTC-USD daily  |  Long-only")
    print(f"  Costs    : 0.1% per trade (commission)")
    print(f"  Walk-forward: IS 2020-2022  /  OOS 2023-2024")

    # Run on the full window so indicators are fully warmed up for the OOS period.
    # IS/OOS split is applied to the resulting equity curve and trade list.
    full = run_backtest(df, **PARAMS)

    IS_END    = pd.Timestamp("2022-12-31")
    OOS_START = pd.Timestamp("2023-01-01")

    is_eq  = full["equity"]["2020-01-01":"2022-12-31"]
    oos_eq = full["equity"]["2023-01-01":"2024-12-31"]

    is_trades  = [t for t in full["trades"] if t["entry_date"] <= IS_END]
    oos_trades = [t for t in full["trades"] if t["entry_date"] >= OOS_START]

    is_res  = period_metrics(is_eq,  is_trades)
    oos_res = period_metrics(oos_eq, oos_trades)

    print_results("IN-SAMPLE  (2020-2022)", is_res)
    ascii_equity(is_res["equity"])

    print_results("OUT-OF-SAMPLE  (2023-2024)", oos_res)
    ascii_equity(oos_res["equity"])

    print("\n" + "="*40)
    print("  NOTE: This is a demonstration of backtesting")
    print("  methodology. EMA crossover is a textbook")
    print("  strategy included to show the full pipeline.")
    print("="*40 + "\n")
