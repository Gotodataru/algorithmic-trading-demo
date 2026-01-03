\# Как расширить систему



\## Добавление нового индикатора



1\. Создайте файл в `src/indicators/`

2\. Реализуйте функцию расчета:

```python

from dataclasses import dataclass

from typing import List

import numpy as np



@dataclass

class MyIndicatorResult:

&nbsp;   value: float

&nbsp;   signal: str



def calculate\_my\_indicator(prices: List\[float], period: int = 14) -> MyIndicatorResult:

&nbsp;   # Реализация индикатора

&nbsp;   pass

