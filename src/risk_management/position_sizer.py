"""
Расчет размера позиции - показывает понимание риск-менеджмента
без реальных формул из продакшена
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class PositionSizeParams:
    """Параметры для расчета размера позиции"""
    account_balance: float
    risk_per_trade: float  # В процентах от баланса
    entry_price: float
    stop_loss: float
    symbol: str

@dataclass
class PositionSizeResult:
    """Результат расчета размера позиции"""
    position_size: float
    notional_value: float
    risk_amount: float
    stop_loss_pct: float

class PositionSizer:
    """
    Калькулятор размера позиции на основе риска
    Демонстрирует принципы мани-менеджмента
    """
    
    def __init__(self, min_position_usdt: float = 10.0):
        self.min_position_usdt = min_position_usdt
    
    def calculate(self, params: PositionSizeParams) -> PositionSizeResult:
        """
        Расчет размера позиции по принципу риска на сделку
        
        Args:
            params: Параметры для расчета
            
        Returns:
            PositionSizeResult: Рассчитанный размер позиции
        """
        # Расчет риска в деньгах
        risk_amount = params.account_balance * (params.risk_per_trade / 100.0)
        
        # Расчет стоп-лосса в процентах
        if params.entry_price > params.stop_loss:
            # Для long позиции
            stop_loss_pct = (params.entry_price - params.stop_loss) / params.entry_price
        else:
            # Для short позиции
            stop_loss_pct = (params.stop_loss - params.entry_price) / params.entry_price
        
        # Расчет размера позиции: риск / (цена * % стоп-лосса)
        if stop_loss_pct > 0:
            position_size = risk_amount / (params.entry_price * stop_loss_pct)
        else:
            position_size = 0.0
        
        # Номинальная стоимость
        notional_value = position_size * params.entry_price
        
        # Проверка минимального размера
        if notional_value < self.min_position_usdt:
            position_size = 0.0
            notional_value = 0.0
        
        return PositionSizeResult(
            position_size=position_size,
            notional_value=notional_value,
            risk_amount=risk_amount,
            stop_loss_pct=stop_loss_pct
        )