"""
Типы ордеров и сигналов для системы исполнения
"""
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


class OrderSide(Enum):
    """Сторона ордера"""
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    """Тип ордера"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderStatus(Enum):
    """Статус ордера"""
    PENDING = "pending"
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass
class OrderSignal:
    """
    Торговый сигнал, генерируемый стратегией.
    """
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: Optional[float] = None
    price: Optional[float] = None
    stop_price: Optional[float] = None
    take_profit: Optional[float] = None
    stop_loss: Optional[float] = None
    timestamp: datetime = None
    confidence: float = 0.5  # Уверенность стратегии в сигнале (0-1)
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def validate(self) -> bool:
        """
        Проверка валидности сигнала.
        
        Returns:
            bool: True если сигнал валиден
        """
        if not self.symbol or not self.side or not self.order_type:
            return False
        
        if self.order_type in [OrderType.LIMIT, OrderType.STOP_LIMIT] and self.price is None:
            return False
            
        if self.order_type in [OrderType.STOP, OrderType.STOP_LIMIT] and self.stop_price is None:
            return False
            
        return True


@dataclass
class Order:
    """
    Исполненный ордер в системе.
    """
    id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: float
    status: OrderStatus
    timestamp: datetime
    filled_quantity: float = 0.0
    average_price: float = 0.0
    commission: float = 0.0
    commission_asset: str = "USDT"
    client_order_id: Optional[str] = None