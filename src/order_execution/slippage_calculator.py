"""
Модуль для расчета проскальзывания (slippage)
"""
import numpy as np
from typing import Tuple

class SlippageCalculator:
    """
    Калькулятор проскальзывания на основе ликвидности
    Демонстрирует понимание факторов исполнения ордеров
    """
    
    def __init__(self, base_slippage_bps: float = 5.0):
        """
        Args:
            base_slippage_bps: Базовое проскальзывание в basis points (0.01%)
        """
        self.base_slippage_bps = base_slippage_bps
    
    def calculate_slippage(self,
                          order_size_usdt: float,
                          daily_volume_usdt: float,
                          orderbook_depth_usdt: float) -> Tuple[float, float]:
        """
        Расчет ожидаемого проскальзывания
        
        Args:
            order_size_usdt: Размер ордера в USDT
            daily_volume_usdt: Дневной объем торгов в USDT
            orderbook_depth_usdt: Глубина стакана на 5 уровней в USDT
            
        Returns:
            Tuple: (slippage_bps, estimated_price_impact)
        """
        if daily_volume_usdt <= 0 or orderbook_depth_usdt <= 0:
            return self.base_slippage_bps, 0.0
        
        # Коэффициент размера ордера к объему
        size_ratio = order_size_usdt / daily_volume_usdt
        
        # Коэффициент размера ордера к глубине стакана
        depth_ratio = order_size_usdt / orderbook_depth_usdt
        
        # Базовое проскальзывание + дополнительное из-за размера
        # В реальной системе здесь была бы более сложная модель
        slippage_bps = self.base_slippage_bps + (depth_ratio * 100)
        
        # Ограничиваем максимальное проскальзывание
        slippage_bps = min(slippage_bps, 50.0)  # Максимум 0.5%
        
        # Расчет impact на цену (упрощенный)
        price_impact = slippage_bps / 10000  # Конвертация bps в проценты
        
        return slippage_bps, price_impact
    
    def estimate_execution_price(self,
                               current_price: float,
                               side: str,
                               slippage_bps: float) -> float:
        """
        Оценка цены исполнения с учетом проскальзывания
        
        Args:
            current_price: Текущая цена
            side: Сторона сделки ('buy' или 'sell')
            slippage_bps: Проскальзывание в bps
            
        Returns:
            float: Ожидаемая цена исполнения
        """
        slippage_pct = slippage_bps / 10000  # 1 bps = 0.01%
        
        if side == 'buy':
            # При покупке платим больше
            return current_price * (1 + slippage_pct)
        else:
            # При продаже получаем меньше
            return current_price * (1 - slippage_pct)