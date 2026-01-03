"""
Тесты для индикаторов
"""
import pytest
import numpy as np
from src.indicators.atr_calculator import calculate_atr, ATRResult
from src.indicators.ema_calculator import calculate_ema, EMAResult

class TestATRCalculator:
    """Тесты для ATR"""
    
    def test_atr_calculation(self):
        """Тест расчета ATR на простых данных"""
        highs = [100, 102, 101, 103]
        lows = [98, 99, 97, 100]
        closes = [99, 101, 100, 102]
        
        result = calculate_atr(highs, lows, closes, period=2)
        
        assert isinstance(result, ATRResult)
        assert result.period == 2
        assert result.value > 0
    
    def test_atr_insufficient_data(self):
        """Тест на недостаточное количество данных"""
        highs = [100]
        lows = [98]
        closes = [99]
        
        with pytest.raises(ValueError):
            calculate_atr(highs, lows, closes, period=14)
    
    def test_atr_constant_prices(self):
        """Тест ATR при постоянных ценах"""
        highs = [100] * 20
        lows = [100] * 20
        closes = [100] * 20
        
        result = calculate_atr(highs, lows, closes, period=14)
        
        assert result.value == 0.0

class TestEMACalculator:
    """Тесты для EMA"""
    
    def test_ema_calculation(self):
        """Тест расчета EMA"""
        prices = [100, 101, 102, 103, 104, 105]
        
        result = calculate_ema(prices, period=3)
        
        assert isinstance(result, EMAResult)
        assert result.period == 3
        assert len(result.values) == len(prices)
        assert all(isinstance(v, float) for v in result.values)
    
    def test_ema_insufficient_data(self):
        """Тест на недостаточное количество данных"""
        prices = [100, 101]
        
        with pytest.raises(ValueError):
            calculate_ema(prices, period=3)
    
    def test_ema_single_price(self):
        """Тест EMA при одной цене"""
        prices = [100] * 10
        
        result = calculate_ema(prices, period=5)
        
        # EMA постоянной цены равна этой цене
        assert all(v == 100.0 for v in result.values)