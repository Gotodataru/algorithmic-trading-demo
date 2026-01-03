"""
Абстрактный провайдер данных - показывает понимание интерфейсов
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class OHLCV:
    """Модель свечи - безопасная структура данных"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

class DataProvider(ABC):
    """
    Абстрактный класс для получения рыночных данных.
    Реализации могут быть для разных бирж (Bybit, Binance и т.д.)
    """
    
    @abstractmethod
    def get_ohlcv(self, 
                  symbol: str, 
                  timeframe: str, 
                  limit: int = 100) -> List[OHLCV]:
        """Получить исторические свечи"""
        pass
    
    @abstractmethod
    def get_orderbook(self, 
                     symbol: str, 
                     depth: int = 10) -> Dict:
        """Получить стакан ордеров"""
        pass
    
    @abstractmethod
    def get_ticker(self, symbol: str) -> Dict[str, float]:
        """Получить текущие цены"""
        pass