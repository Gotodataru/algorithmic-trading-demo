"""
Демонстрация работы всей системы.
Показывает как компоненты взаимодействуют друг с другом.
"""
import asyncio
import yaml
from typing import Dict, Any
from datetime import datetime, timedelta

from src.data_provider import BinanceDataProvider, OHLCV
from src.indicators import calculate_atr, calculate_ema
from src.strategies import SimpleMAStrategy, StrategyConfig
from src.order_execution import OrderSignal, OrderSide, OrderType
from src.risk_management import PositionSizer, PositionSizeParams


class TradingSystemDemo:
    """
    Демонстрация работы алгоритмической торговой системы.
    Показывает взаимодействие всех модулей.
    """
    
    def __init__(self, config_path: str = 'config_example.yaml'):
        self.config = self._load_config(config_path)
        self.data_provider = None
        self.strategies = []
        self.position_sizer = PositionSizer(
            min_position_usdt=self.config['risk']['min_position_size']
        )
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Загрузка конфигурации из YAML файла.
        
        Args:
            config_path: Путь к файлу конфигурации
            
        Returns:
            Словарь с конфигурацией
        """
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Config file {config_path} not found. Using default config.")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Получение конфигурации по умолчанию"""
        return {
            'risk': {
                'risk_per_trade': 1.0,
                'max_daily_risk': 2.0,
                'min_position_size': 10
            },
            'data': {
                'default_exchange': 'binance',
                'symbols': ['BTC/USDT', 'ETH/USDT']
            }
        }
    
    async def initialize(self):
        """Инициализация системы"""
        print("Initializing Trading System...")
        
        # Инициализация провайдера данных
        self.data_provider = BinanceDataProvider()
        print(f"Data Provider initialized: {self.data_provider.__class__.__name__}")
        
        # Инициализация стратегий
        for symbol in self.config['data']['symbols'][:2]:  # Берем первые 2 символа
            strategy_config = StrategyConfig(
                name=f"MA_Strategy_{symbol}",
                symbol=symbol,
                timeframe='1h',
                parameters={
                    'fast_period': 9,
                    'slow_period': 21
                }
            )
            
            strategy = SimpleMAStrategy(strategy_config)
            self.strategies.append(strategy)
            print(f"Strategy initialized: {strategy.name}")
        
        print("System initialization complete!\n")
    
    async def run_simulation(self, days: int = 7):
        """
        Запуск симуляции работы системы.
        
        Args:
            days: Количество дней для симуляции
        """
        print(f"Starting {days}-day simulation...")
        
        for strategy in self.strategies:
            print(f"\n--- Analyzing {strategy.symbol} ---")
            
            # Получаем исторические данные
            data = await self.data_provider.get_ohlcv(
                symbol=strategy.symbol,
                timeframe=strategy.timeframe,
                limit=100
            )
            
            if not data:
                print(f"No data for {strategy.symbol}")
                continue
            
            # Анализируем данные стратегией
            signal = strategy.analyze(data)
            
            if signal:
                print(f"Signal generated: {signal.side.value.upper()} {signal.symbol}")
                print(f"Confidence: {signal.confidence:.2f}")
                
                # Расчет размера позиции
                account_balance = 10000  # Демо-значение
                stop_loss = data[-1].close * 0.98  # Демо: стоп-лосс на 2%
                
                position_params = PositionSizeParams(
                    account_balance=account_balance,
                    risk_per_trade=self.config['risk']['risk_per_trade'],
                    entry_price=data[-1].close,
                    stop_loss=stop_loss,
                    symbol=strategy.symbol
                )
                
                position_size = self.position_sizer.calculate(position_params)
                
                print(f"Position size calculated:")
                print(f"  Size: {position_size.position_size:.6f}")
                print(f"  Notional: ${position_size.notional_value:.2f}")
                print(f"  Risk: ${position_size.risk_amount:.2f}")
                
                # Расчет индикаторов для демонстрации
                highs = [c.high for c in data]
                lows = [c.low for c in data]
                closes = [c.close for c in data]
                
                atr_result = calculate_atr(highs, lows, closes, period=14)
                print(f"  ATR: {atr_result.value:.2f}")
                
            else:
                print("No trading signal generated")
            
            # Показываем статус стратегии
            status = strategy.get_status()
            print(f"Strategy status: {status['name']} - Active: {status['active']}")
        
        print("\nSimulation complete!")
    
    async def cleanup(self):
        """Очистка ресурсов"""
        if self.data_provider:
            await self.data_provider.close()
        print("\nSystem cleanup complete.")


async def main():
    """Основная функция демо"""
    print("=" * 60)
    print("ALGORITHMIC TRADING SYSTEM DEMONSTRATION")
    print("=" * 60)
    
    # Создаем и запускаем систему
    system = TradingSystemDemo()
    
    try:
        await system.initialize()
        await system.run_simulation(days=3)
    except Exception as e:
        print(f"Error during simulation: {e}")
    finally:
        await system.cleanup()
    
    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())