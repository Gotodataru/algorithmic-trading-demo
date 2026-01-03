"""
Модуль для логирования сделок
"""
import json
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional
from pathlib import Path

@dataclass
class TradeRecord:
    """Запись о сделке для логирования"""
    trade_id: str
    symbol: str
    side: str
    entry_price: float
    exit_price: Optional[float]
    quantity: float
    entry_time: datetime
    exit_time: Optional[datetime]
    stop_loss: float
    take_profit: float
    risk_reward_ratio: float
    # В реальной системе здесь были бы реальные метрики PnL

class TradeLogger:
    """
    Логгер сделок для сбора данных и анализа
    Демонстрирует подход к сбору метрик
    """
    
    def __init__(self, log_dir: str = "./logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Имя файла лога основано на дате
        self.log_file = self.log_dir / f"trades_{datetime.now().strftime('%Y%m%d')}.jsonl"
    
    def log_trade(self, trade: TradeRecord):
        """
        Запись сделки в лог
        
        Args:
            trade: Объект TradeRecord
        """
        # Конвертируем в словарь
        trade_dict = asdict(trade)
        
        # Конвертируем datetime в строку для JSON
        for key in ['entry_time', 'exit_time']:
            if trade_dict[key] is not None:
                trade_dict[key] = trade_dict[key].isoformat()
        
        # Записываем в файл в формате JSONL
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(trade_dict, ensure_ascii=False) + '\n')
    
    def read_trades(self, date: Optional[datetime] = None) -> List[TradeRecord]:
        """
        Чтение сделок из лога
        
        Args:
            date: Дата для чтения (если None, читает текущий день)
            
        Returns:
            List[TradeRecord]: Список сделок
        """
        if date is None:
            date = datetime.now()
        
        log_file = self.log_dir / f"trades_{date.strftime('%Y%m%d')}.jsonl"
        
        if not log_file.exists():
            return []
        
        trades = []
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    trade_dict = json.loads(line)
                    
                    # Конвертируем строки обратно в datetime
                    for key in ['entry_time', 'exit_time']:
                        if trade_dict[key] is not None:
                            trade_dict[key] = datetime.fromisoformat(trade_dict[key])
                    
                    trades.append(TradeRecord(**trade_dict))
        
        return trades