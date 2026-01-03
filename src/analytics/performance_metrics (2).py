"""
Модуль для расчета метрик производительности
"""
import numpy as np
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class PerformanceMetrics:
    """Метрики производительности торговой системы"""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    avg_win: float  # В процентах
    avg_loss: float  # В процентах
    profit_factor: float
    sharpe_ratio: Optional[float]
    max_drawdown: float  # В процентах

def calculate_sharpe_ratio(returns: List[float], 
                          risk_free_rate: float = 0.0) -> float:
    """
    Расчет коэффициента Шарпа
    
    Args:
        returns: Список доходностей в процентах
        risk_free_rate: Безрисковая ставка в процентах
        
    Returns:
        float: Коэффициент Шарпа
    """
    if not returns:
        return 0.0
    
    returns_array = np.array(returns)
    
    # Избыточная доходность
    excess_returns = returns_array - risk_free_rate
    
    # Стандартное отклонение
    std_dev = np.std(excess_returns)
    
    if std_dev == 0:
        return 0.0
    
    # Коэффициент Шарпа
    sharpe = np.mean(excess_returns) / std_dev
    
    # Годовой коэффициент (предполагаем 252 торговых дня)
    sharpe_annualized = sharpe * np.sqrt(252)
    
    return float(sharpe_annualized)

def calculate_max_drawdown(equity_curve: List[float]) -> float:
    """
    Расчет максимальной просадки
    
    Args:
        equity_curve: Кривая капитала
        
    Returns:
        float: Максимальная просадка в процентах
    """
    if not equity_curve:
        return 0.0
    
    equity_array = np.array(equity_curve)
    
    # Вычисляем running maximum
    running_max = np.maximum.accumulate(equity_array)
    
    # Вычисляем просадки
    drawdowns = (equity_array - running_max) / running_max
    
    # Максимальная просадка (минимальное значение, отрицательное)
    max_dd = np.min(drawdowns) * 100  # В процентах
    
    return float(max_dd)