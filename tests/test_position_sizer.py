"""
Тесты для калькулятора размера позиции
"""
import pytest
from src.risk_management.position_sizer import (
    PositionSizer, 
    PositionSizeParams, 
    PositionSizeResult
)

class TestPositionSizer:
    """Тесты для PositionSizer"""
    
    def test_position_sizer_initialization(self):
        """Тест инициализации PositionSizer"""
        sizer = PositionSizer(min_position_usdt=10.0)
        assert sizer.min_position_usdt == 10.0
    
    def test_long_position_calculation(self):
        """Тест расчета long позиции"""
        sizer = PositionSizer(min_position_usdt=10.0)
        
        params = PositionSizeParams(
            account_balance=10000.0,
            risk_per_trade=1.0,  # 1%
            entry_price=100.0,
            stop_loss=95.0,
            symbol="BTC/USDT"
        )
        
        result = sizer.calculate(params)
        
        assert isinstance(result, PositionSizeResult)
        assert result.position_size > 0
        assert result.notional_value > 0
        assert result.risk_amount == 100.0  # 1% от 10000
        assert result.stop_loss_pct == 0.05  # (100-95)/100
        
        # Проверяем формулу: position_size = risk_amount / (entry_price * stop_loss_pct)
        expected_size = 100.0 / (100.0 * 0.05)  # 20
        assert abs(result.position_size - expected_size) < 0.001
    
    def test_short_position_calculation(self):
        """Тест расчета short позиции"""
        sizer = PositionSizer(min_position_usdt=10.0)
        
        params = PositionSizeParams(
            account_balance=10000.0,
            risk_per_trade=1.0,
            entry_price=100.0,
            stop_loss=105.0,  # Stop loss выше для short
            symbol="BTC/USDT"
        )
        
        result = sizer.calculate(params)
        
        assert result.stop_loss_pct == 0.05  # (105-100)/100
        
        # Для short позиции также должен быть положительный размер
        assert result.position_size > 0
    
    def test_zero_stop_loss(self):
        """Тест с нулевым стоп-лоссом"""
        sizer = PositionSizer(min_position_usdt=10.0)
        
        params = PositionSizeParams(
            account_balance=10000.0,
            risk_per_trade=1.0,
            entry_price=100.0,
            stop_loss=100.0,  # Стоп-лосс равен цене входа
            symbol="BTC/USDT"
        )
        
        result = sizer.calculate(params)
        
        assert result.stop_loss_pct == 0.0
        assert result.position_size == 0.0
        assert result.notional_value == 0.0
    
    def test_minimum_position_size(self):
        """Тест минимального размера позиции"""
        sizer = PositionSizer(min_position_usdt=1000.0)  # Высокий минимум
        
        params = PositionSizeParams(
            account_balance=1000.0,  # Маленький баланс
            risk_per_trade=1.0,
            entry_price=100.0,
            stop_loss=95.0,
            symbol="BTC/USDT"
        )
        
        result = sizer.calculate(params)
        
        # Позиция должна быть 0, потому что неional_value < min_position_usdt
        assert result.position_size == 0.0
        assert result.notional_value == 0.0