\# Руководство по созданию стратегий



\## Обзор

Стратегии в системе реализуются через наследование от `BaseStrategy`.



\## Создание новой стратегии



\### 1. Создайте файл стратегии

```python

\# src/strategies/my\_strategy.py

from typing import List, Optional

from .base\_strategy import BaseStrategy, StrategyConfig

from src.data\_provider import OHLCV

from src.order\_execution import OrderSignal



class MyStrategy(BaseStrategy):

&nbsp;   def \_\_init\_\_(self, config: StrategyConfig):

&nbsp;       super().\_\_init\_\_(config)

&nbsp;       # Инициализация параметров

&nbsp;       

&nbsp;   def analyze(self, data: List\[OHLCV]) -> Optional\[OrderSignal]:

&nbsp;       # Логика анализа

&nbsp;       pass

&nbsp;       

&nbsp;   def should\_exit(self, data: List\[OHLCV], current\_position) -> Optional\[OrderSignal]:

&nbsp;       # Логика выхода

&nbsp;       pass

