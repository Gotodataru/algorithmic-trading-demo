"""
Пример расчета EMA - простой индикатор
"""
import numpy as np
from typing import List
from dataclasses import dataclass

@dataclass
class EMAResult:
    """Результат расчета EMA"""
    values: List[float]
    period: int

def calculate_ema(prices: List[float], period: int = 20) -> EMAResult:
    """
    Расчет Exponential Moving Average (EMA)
    
    Args:
        prices: Список цен
        period: Период для расчета EMA
        
    Returns:
        EMAResult: Объект со значениями EMA и периодом
    """
    if len(prices) < period:
        raise ValueError(f"Недостаточно данных для расчета EMA. Нужно минимум {period} цен")
    
    # Конвертируем в numpy
    prices_array = np.array(prices, dtype=float)
    
    # Коэффициент сглаживания
    alpha = 2 / (period + 1)
    
    # Инициализируем массив для EMA
    ema = np.zeros_like(prices_array)
    ema[0] = prices_array[0]
    
    # Рекуррентный расчет EMA
    for i in range(1, len(prices_array)):
        ema[i] = alpha * prices_array[i] + (1 - alpha) * ema[i-1]
    
    return EMAResult(values=ema.tolist(), period=period)