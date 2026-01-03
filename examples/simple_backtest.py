"""
Пример простого бэктеста - показывает подход к тестированию
без реальной стратегии
"""
import pandas as pd
import numpy as np
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class Trade:
    """Модель сделки для бэктеста"""
    entry_price: float
    exit_price: float
    entry_time: pd.Timestamp
    exit_time: pd.Timestamp
    side: str  # 'buy' или 'sell'

class BacktestEngine:
    """
    Движок для бэктестирования стратегий
    Демонстрирует подход к тестированию на исторических данных
    """
    
    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.trades: List[Trade] = []
    
    def run(self, 
            data: pd.DataFrame,
            strategy_func,  # Функция стратегии (не реализована в демо)
            **kwargs) -> Dict[str, float]:
        """
        Запуск бэктеста
        
        Args:
            data: DataFrame с историческими данными
            strategy_func: Функция стратегии (принимает данные, возвращает сигнал)
            **kwargs: Дополнительные параметры
            
        Returns:
            Dict: Метрики производительности
        """
        if data.empty:
            return {"error": "No data provided"}
        
        # Здесь была бы логика стратегии
        # В демо просто создаем фиктивные сделки
        self._create_dummy_trades(data)
        
        # Расчет метрик
        metrics = self._calculate_metrics()
        
        return metrics
    
    def _create_dummy_trades(self, data: pd.DataFrame):
        """Создание фиктивных сделок для демонстрации"""
        # В реальном коде здесь была бы логика стратегии
        # В демо просто создаем несколько случайных сделок
        sample_size = min(10, len(data))
        
        for i in range(sample_size):
            if i % 3 == 0:  # Каждая третья строка - сделка
                trade = Trade(
                    entry_price=data['close'].iloc[i],
                    exit_price=data['close'].iloc[i] * 1.02,  # +2%
                    entry_time=data.index[i],
                    exit_time=data.index[i] + pd.Timedelta(hours=1),
                    side='buy'
                )
                self.trades.append(trade)
    
    def _calculate_metrics(self) -> Dict[str, float]:
        """Расчет метрик производительности"""
        if not self.trades:
            return {"total_trades": 0, "win_rate": 0.0}
        
        # Простые метрики
        total_trades = len(self.trades)
        winning_trades = sum(1 for t in self.trades 
                           if t.exit_price > t.entry_price)
        
        win_rate = winning_trades / total_trades if total_trades > 0 else 0.0
        
        return {
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "win_rate": win_rate,
            "avg_return_pct": 2.0  # Фиктивное значение
        }

# Пример использования
if __name__ == "__main__":
    # Создаем фиктивные данные
    dates = pd.date_range('2024-01-01', periods=100, freq='H')
    data = pd.DataFrame({
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 101,
        'low': np.random.randn(100).cumsum() + 99,
        'close': np.random.randn(100).cumsum() + 100,
        'volume': np.random.randint(100, 1000, 100)
    }, index=dates)
    
    # Запуск бэктеста
    engine = BacktestEngine(initial_capital=10000)
    results = engine.run(data, strategy_func=lambda x: None)
    
    print("Backtest Results:")
    for key, value in results.items():
        print(f"  {key}: {value}")