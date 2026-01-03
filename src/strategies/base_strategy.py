"""
Базовый класс для всех стратегий - показывает архитектурный подход
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass

from src.data_provider import OHLCV
from src.order_execution import OrderSignal, OrderType, OrderSide


@dataclass
class StrategyConfig:
    """Конфигурация стратегии"""
    name: str
    symbol: str
    timeframe: str
    parameters: dict


class BaseStrategy(ABC):
    """
    Абстрактный базовый класс для торговых стратегий.
    Все стратегии должны наследоваться от этого класса.
    """
    
    def __init__(self, config: StrategyConfig):
        self.config = config
        self.name = config.name
        self.symbol = config.symbol
        self.timeframe = config.timeframe
        self.parameters = config.parameters
        
    @abstractmethod
    def analyze(self, data: List[OHLCV]) -> Optional[OrderSignal]:
        """
        Анализ рыночных данных и генерация торгового сигнала.
        
        Args:
            data: Список OHLCV свечей для анализа
            
        Returns:
            OrderSignal или None, если сигнала нет
        """
        pass
    
    @abstractmethod
    def should_exit(self, data: List[OHLCV], current_position) -> Optional[OrderSignal]:
        """
        Проверка условий для выхода из позиции.
        
        Args:
            data: Актуальные рыночные данные
            current_position: Текущая открытая позиция
            
        Returns:
            OrderSignal для выхода или None
        """
        pass
    
    def update_parameters(self, new_params: dict):
        """
        Обновление параметров стратегии.
        
        Args:
            new_params: Новые параметры
        """
        self.parameters.update(new_params)
        
    def get_status(self) -> dict:
        """
        Получение текущего статуса стратегии.
        
        Returns:
            Словарь с информацией о стратегии
        """
        return {
            'name': self.name,
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'parameters': self.parameters,
            'active': True
        }