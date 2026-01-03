"""
Модуль для контроля дневных лимитов
"""
from dataclasses import dataclass
from datetime import datetime, date
from typing import Dict

@dataclass
class DailyStats:
    """Статистика за день"""
    date: date
    trades_count: int
    total_risk: float
    pnl: float  # В демо не используется реальный PnL

class DailyLimits:
    """
    Контроль дневных лимитов убытков и количества сделок
    """
    
    def __init__(self, 
                 max_daily_trades: int = 10,
                 max_daily_risk: float = 2.0):  # 2% от капитала
        self.max_daily_trades = max_daily_trades
        self.max_daily_risk = max_daily_risk
        self.daily_stats: Dict[date, DailyStats] = {}
        self.current_date = date.today()
        
        # Инициализируем статистику на сегодня
        self._init_today_stats()
    
    def _init_today_stats(self):
        """Инициализация статистики на текущий день"""
        if self.current_date not in self.daily_stats:
            self.daily_stats[self.current_date] = DailyStats(
                date=self.current_date,
                trades_count=0,
                total_risk=0.0,
                pnl=0.0
            )
    
    def can_trade(self, risk_amount: float) -> bool:
        """
        Проверка, можно ли открывать сделку с учетом дневных лимитов
        
        Args:
            risk_amount: Размер риска в сделке (в деньгах)
            
        Returns:
            bool: True если сделка разрешена
        """
        # Обновляем текущую дату
        today = date.today()
        if today != self.current_date:
            self.current_date = today
            self._init_today_stats()
        
        stats = self.daily_stats[today]
        
        # Проверяем лимит на количество сделок
        if stats.trades_count >= self.max_daily_trades:
            return False
        
        # Проверяем лимит на суммарный риск
        # В демо risk_amount в процентах, но в реальной системе был бы в деньгах
        if stats.total_risk + risk_amount > self.max_daily_risk:
            return False
        
        return True
    
    def record_trade(self, risk_amount: float):
        """
        Запись информации о сделке
        
        Args:
            risk_amount: Размер риска в сделке
        """
        today = date.today()
        if today not in self.daily_stats:
            self._init_today_stats()
        
        stats = self.daily_stats[today]
        stats.trades_count += 1
        stats.total_risk += risk_amount
    
    def get_today_stats(self) -> DailyStats:
        """Получить статистику на текущий день"""
        today = date.today()
        if today not in self.daily_stats:
            self._init_today_stats()
        return self.daily_stats[today]