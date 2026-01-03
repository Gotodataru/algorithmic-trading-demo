"""
Strategies module - торговые стратегии для алгоритмического трейдинга
"""

from .base_strategy import BaseStrategy, StrategyConfig
from .simple_ma_strategy import SimpleMAStrategy
from .my_strategy import MyStrategy

__all__ = [
    'BaseStrategy',
    'StrategyConfig',
    'SimpleMAStrategy',
]