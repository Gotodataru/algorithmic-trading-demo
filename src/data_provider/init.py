# src/data_provider/__init__.py
"""
Data Provider module - получение рыночных данных с бирж
"""

from .base_provider import DataProvider, OHLCV
from .ccxt_example import CCXTDataProvider
from .binance_provider import BinanceDataProvider  # ДОБАВЬ ЭТУ СТРОКУ

__all__ = [
    'DataProvider',
    'OHLCV',
    'CCXTDataProvider',
    'BinanceDataProvider',  
]