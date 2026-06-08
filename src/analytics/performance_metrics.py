import numpy as np
import pandas as pd
from dataclasses import dataclass


@dataclass
class BacktestMetrics:
    total_return_pct: float
    sharpe_ratio: float
    max_drawdown_pct: float
    win_rate: float
    total_trades: int
    avg_trade_pct: float

    def __str__(self):
        return (
            f"  Total return : {self.total_return_pct:+.1f}%\n"
            f"  Sharpe ratio : {self.sharpe_ratio:.3f}\n"
            f"  Max drawdown : {self.max_drawdown_pct:.1f}%\n"
            f"  Win rate     : {self.win_rate:.1f}%\n"
            f"  Total trades : {self.total_trades}\n"
            f"  Avg trade    : {self.avg_trade_pct:+.3f}%"
        )


def calculate_metrics(equity_curve: pd.Series, trades: list) -> BacktestMetrics:
    returns = equity_curve.pct_change().dropna()

    total_return = (equity_curve.iloc[-1] / equity_curve.iloc[0] - 1) * 100

    sharpe = 0.0
    if len(returns) > 1 and returns.std() > 0:
        sharpe = (returns.mean() / returns.std()) * np.sqrt(252)

    rolling_max = equity_curve.cummax()
    drawdown = (equity_curve - rolling_max) / rolling_max
    max_dd = drawdown.min() * 100

    if trades:
        win_rate = sum(1 for t in trades if t['pnl_pct'] > 0) / len(trades) * 100
        avg_trade = float(np.mean([t['pnl_pct'] for t in trades]))
    else:
        win_rate = 0.0
        avg_trade = 0.0

    return BacktestMetrics(
        total_return_pct=round(total_return, 2),
        sharpe_ratio=round(sharpe, 3),
        max_drawdown_pct=round(max_dd, 2),
        win_rate=round(win_rate, 1),
        total_trades=len(trades),
        avg_trade_pct=round(avg_trade, 3),
    )
