"""
EMA crossover strategy with RSI filter and volume confirmation.
Entry: fast EMA crosses slow EMA + RSI not extreme + volume spike.
Exit: opposite crossover or ATR-based stop-loss.
"""
from typing import List, Optional
import numpy as np

from .base_strategy import BaseStrategy, StrategyConfig
from src.data_provider import OHLCV
from src.order_execution import OrderSignal, OrderSide, OrderType
from src.indicators.ema_calculator import calculate_ema
from src.indicators.rsi_calculator import calculate_rsi


class SimpleMAStrategy(BaseStrategy):

    def __init__(self, config: StrategyConfig):
        super().__init__(config)
        self.fast_period   = self.parameters.get('fast_period', 10)
        self.slow_period   = self.parameters.get('slow_period', 30)
        self.rsi_period    = self.parameters.get('rsi_period', 14)
        self.rsi_overbought = self.parameters.get('rsi_overbought', 65)
        self.rsi_oversold   = self.parameters.get('rsi_oversold', 35)
        self.volume_mult   = self.parameters.get('volume_mult', 1.5)
        self.atr_stop_mult = self.parameters.get('atr_stop_mult', 2.0)
        self._position_side = None

    def analyze(self, data: List[OHLCV]) -> Optional[OrderSignal]:
        min_len = self.slow_period + self.rsi_period + 1
        if len(data) < min_len:
            return None

        closes  = [c.close  for c in data]
        volumes = [c.volume for c in data]

        fast = np.array(calculate_ema(closes, self.fast_period).values)
        slow = np.array(calculate_ema(closes, self.slow_period).values)
        rsi  = calculate_rsi(closes, self.rsi_period).values

        vol_arr = np.array(volumes, dtype=float)
        vol_ma  = vol_arr[-20:].mean()

        curr_rsi    = rsi[-1]
        curr_vol    = vol_arr[-1]
        curr_cross  = fast[-1] - slow[-1]
        prev_cross  = fast[-2] - slow[-2]
        volume_ok   = curr_vol > vol_ma * self.volume_mult

        # Long: crossover up + RSI not overbought + volume spike
        if (prev_cross <= 0 and curr_cross > 0
                and curr_rsi < self.rsi_overbought
                and volume_ok):
            self._position_side = 'long'
            return OrderSignal(
                symbol=self.symbol,
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                confidence=self._signal_confidence(curr_rsi, curr_vol, vol_ma),
            )

        # Short: crossover down + RSI not oversold + volume spike
        if (prev_cross >= 0 and curr_cross < 0
                and curr_rsi > self.rsi_oversold
                and volume_ok):
            self._position_side = 'short'
            return OrderSignal(
                symbol=self.symbol,
                side=OrderSide.SELL,
                order_type=OrderType.MARKET,
                confidence=self._signal_confidence(curr_rsi, curr_vol, vol_ma),
            )

        return None

    def should_exit(self, data: List[OHLCV], current_position) -> Optional[OrderSignal]:
        if not current_position or len(data) < 15:
            return None

        closes = np.array([c.close for c in data])
        highs  = np.array([c.high  for c in data])
        lows   = np.array([c.low   for c in data])

        atr  = self._calc_atr(highs, lows, closes, 14)
        stop = atr * self.atr_stop_mult

        if current_position.side == 'long':
            if closes[-1] < current_position.entry_price - stop:
                return OrderSignal(
                    symbol=self.symbol,
                    side=OrderSide.SELL,
                    order_type=OrderType.MARKET,
                    confidence=1.0,
                )
        else:
            if closes[-1] > current_position.entry_price + stop:
                return OrderSignal(
                    symbol=self.symbol,
                    side=OrderSide.BUY,
                    order_type=OrderType.MARKET,
                    confidence=1.0,
                )
        return None

    def _signal_confidence(self, rsi: float, vol: float, vol_ma: float) -> float:
        rsi_strength = abs(rsi - 50) / 50          # 0..1, higher = stronger trend
        vol_strength = min(vol / (vol_ma * 3), 1.0) # 0..1, cap at 3x average
        return round(0.5 + 0.25 * rsi_strength + 0.25 * vol_strength, 2)

    @staticmethod
    def _calc_atr(highs, lows, closes, period=14) -> float:
        tr = np.maximum(
            highs[1:] - lows[1:],
            np.maximum(
                np.abs(highs[1:] - closes[:-1]),
                np.abs(lows[1:] - closes[:-1]),
            ),
        )
        return float(tr[-period:].mean())

    def get_status(self) -> dict:
        status = super().get_status()
        status.update({
            'fast_period': self.fast_period,
            'slow_period': self.slow_period,
            'rsi_period':  self.rsi_period,
            'position_side': self._position_side,
        })
        return status
