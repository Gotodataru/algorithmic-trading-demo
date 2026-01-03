"# src/data_provider/binance_provider.py
"""
Реализация DataProvider для Binance.
"""
from typing import List, Dict, Optional
from datetime import datetime

from .base_provider import DataProvider, OHLCV


class BinanceDataProvider(DataProvider):
    """
    Провайдер данных для Binance.
    Демо-версия без реального подключения к API.
    """
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        """
        Инициализация провайдера.
        
        Args:
            api_key: API ключ (не используется в демо)
            api_secret: API секрет (не используется в демо)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self._cache = {}
        
    def get_ohlcv(self, 
                 symbol: str, 
                 timeframe: str = '1h', 
                 limit: int = 100) -> List[OHLCV]:
        """
        Получение демо-данных OHLCV.
        В реальной системе здесь было бы подключение к API.
        """
        print(f"[DEMO] Fetching OHLCV for {symbol} ({timeframe}, limit={limit})")
        
        # Создаем демо-данные
        import random
        from datetime import datetime, timedelta
        
        result = []
        base_price = 50000.0 if 'BTC' in symbol else 3000.0
        base_time = datetime.now() - timedelta(hours=limit)
        
        for i in range(limit):
            open_price = base_price + random.uniform(-100, 100)
            close_price = open_price + random.uniform(-50, 50)
            high_price = max(open_price, close_price) + random.uniform(0, 50)
            low_price = min(open_price, close_price) - random.uniform(0, 50)
            
            candle = OHLCV(
                timestamp=base_time + timedelta(hours=i),
                open=open_price,
                high=high_price,
                low=low_price,
                close=close_price,
                volume=random.uniform(100, 1000)
            )
            result.append(candle)
        
        return result
    
    def get_orderbook(self, 
                     symbol: str, 
                     depth: int = 10) -> Dict:
        """
        Демо-стакан ордеров.
        """
        print(f"[DEMO] Fetching orderbook for {symbol} (depth={depth})")
        
        # Демо-данные стакана
        import random
        
        bids = []
        asks = []
        base_price = 50000.0 if 'BTC' in symbol else 3000.0
        
        for i in range(depth):
            bid_price = base_price - (i * 0.1)
            ask_price = base_price + (i * 0.1)
            
            bids.append([bid_price, random.uniform(0.1, 1.0)])
            asks.append([ask_price, random.uniform(0.1, 1.0)])
        
        return {
            'bids': bids,
            'asks': asks,
            'symbol': symbol,
            'timestamp': int(datetime.now().timestamp() * 1000)
        }
    
    def get_ticker(self, symbol: str) -> Dict[str, float]:
        """
        Демо-тикер.
        """
        print(f"[DEMO] Fetching ticker for {symbol}")
        
        import random
        base_price = 50000.0 if 'BTC' in symbol else 3000.0
        
        return {
            'last': base_price + random.uniform(-100, 100),
            'bid': base_price - random.uniform(0, 10),
            'ask': base_price + random.uniform(0, 10),
            'high': base_price + random.uniform(100, 200),
            'low': base_price - random.uniform(100, 200),
            'volume': random.uniform(1000, 10000),
            'symbol': symbol
        }
    
    async def close(self):
        """Закрытие соединения"""
        print("[DEMO] Closing data provider")