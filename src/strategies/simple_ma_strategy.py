"""
Пример простой стратегии на скользящих средних (без реальной логики)
Для демонстрации архитектуры
"""
from typing import List, Optional
import numpy as np
from .base_strategy import BaseStrategy, StrategyConfig
from src.data_provider import OHLCV
from src.order_execution import OrderSignal, OrderSide, OrderType


class SimpleMAStrategy(BaseStrategy):
    """
    Демо-стратегия на основе двух скользящих средних.
    Показывает как может выглядеть реализация стратегии.
    """
    
    def __init__(self, config: StrategyConfig):
        super().__init__(config)
        self.fast_period = self.parameters.get('fast_period', 9)
        self.slow_period = self.parameters.get('slow_period', 21)
        self.prev_fast_ma = None
        self.prev_slow_ma = None
        
    def analyze(self, data: List[OHLCV]) -> Optional[OrderSignal]:
        """
        Анализ с использованием двух EMA.
        В демо-версии логика упрощена.
        """
        if len(data) < max(self.fast_period, self.slow_period):
            return None
        
        # Извлекаем цены закрытия
        closes = [candle.close for candle in data]
        
        # Рассчитываем EMA (упрощенный расчет для демо)
        fast_ma = self._calculate_ema(closes, self.fast_period)
        slow_ma = self._calculate_ema(closes, self.slow_period)
        
        # Логика пересечения (демо-версия)
        signal = None
        
        if self.prev_fast_ma is not None and self.prev_slow_ma is not None:
            # Быстрая EMA пересекает медленную снизу вверх
            if (self.prev_fast_ma <= self.prev_slow_ma and 
                fast_ma > slow_ma):
                signal = OrderSignal(
                    symbol=self.symbol,
                    side=OrderSide.BUY,
                    order_type=OrderType.MARKET,
                    confidence=0.6  # Демо-значение
                )
                
            # Быстрая EMA пересекает медленную сверху вниз
            elif (self.prev_fast_ma >= self.prev_slow_ma and 
                  fast_ma < slow_ma):
                signal = OrderSignal(
                    symbol=self.symbol,
                    side=OrderSide.SELL,
                    order_type=OrderType.MARKET,
                    confidence=0.6  # Демо-значение
                )
        
        # Сохраняем текущие значения для следующего вызова
        self.prev_fast_ma = fast_ma
        self.prev_slow_ma = slow_ma
        
        return signal
    
    def should_exit(self, data: List[OHLCV], current_position) -> Optional[OrderSignal]:
        """
        Проверка условий выхода.
        В демо-версии используется простой стоп-лосс по ATR.
        """
        if not current_position:
            return None
        
        # В демо-версии возвращаем None
        # В реальной системе здесь была бы логика выхода
        return None
    
    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """
        Упрощенный расчет EMA для демонстрации.
        
        Args:
            prices: Список цен
            period: Период EMA
            
        Returns:
            Значение EMA
        """
        if len(prices) < period:
            return prices[-1] if prices else 0.0
        
        # Простое SMA для демо
        recent_prices = prices[-period:]
        return sum(recent_prices) / len(recent_prices)
    
    def get_status(self) -> dict:
        """Дополненный статус стратегии"""
        base_status = super().get_status()
        base_status.update({
            'fast_period': self.fast_period,
            'slow_period': self.slow_period,
            'prev_fast_ma': self.prev_fast_ma,
            'prev_slow_ma': self.prev_slow_ma
        })
        return base_status