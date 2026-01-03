"""
Пример расчета ATR - показывает понимание технического анализа
без раскрытия торговой логики
"""
import numpy as np
from typing import List
from dataclasses import dataclass

@dataclass
class ATRResult:
    """Результат расчета ATR"""
    value: float
    period: int

def calculate_atr(highs: List[float], 
                  lows: List[float], 
                  closes: List[float], 
                  period: int = 14) -> ATRResult:
    """
    Расчет Average True Range (ATR)
    
    Args:
        highs: Список максимальных цен
        lows: Список минимальных цен
        closes: Список цен закрытия
        period: Период для расчета
        
    Returns:
        ATRResult: Объект с значением ATR и периодом
    """
    if len(highs) < period or len(lows) < period or len(closes) < period:
        raise ValueError(f"Недостаточно данных для расчета ATR. Нужно минимум {period} баров")
    
    # Конвертируем в numpy для эффективных вычислений
    high = np.array(highs[-period:], dtype=float)
    low = np.array(lows[-period:], dtype=float)
    close = np.array(closes[-period:], dtype=float)
    
    # Сдвигаем close на один бар назад
    prev_close = np.roll(close, 1)
    prev_close[0] = close[0]  # Первый элемент не сдвигаем
    
    # True Range = max(high-low, abs(high-prev_close), abs(prev_close-low))
    tr1 = high - low
    tr2 = np.abs(high - prev_close)
    tr3 = np.abs(prev_close - low)
    
    true_range = np.maximum(np.maximum(tr1, tr2), tr3)
    
    # Расчет ATR как среднее TR за период
    atr_value = np.mean(true_range)
    
    return ATRResult(value=float(atr_value), period=period)