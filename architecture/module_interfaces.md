


# Интерфейсы модулей

## Data Provider

python
class DataProvider(ABC):
    @abstractmethod
    def get_ohlcv(self, symbol: str, timeframe: str, limit: int) -> List[OHLCV]:
        pass
    
    @abstractmethod
    def get_orderbook(self, symbol: str, depth: int) -> OrderBook:
        pass
Strategy Engine
python
class Strategy(ABC):
    @abstractmethod
    def calculate_signals(self, data: MarketData) -> Optional[TradeSignal]:
        pass
Risk Manager
python
class RiskManager(ABC):
    @abstractmethod
    def validate_trade(self, signal: TradeSignal, context: TradeContext) -> bool:
        pass
    
    @abstractmethod
    def calculate_position_size(self, signal: TradeSignal) -> float:
        pass
Order Executor
python
class OrderExecutor(ABC):
    @abstractmethod
    def execute_order(self, order: Order) -> ExecutionResult:
        pass
Analytics Collector
python
class AnalyticsCollector(ABC):
    @abstractmethod
    def log_trade(self, trade: ExecutedTrade):
        pass
    
    @abstractmethod
    def get_performance_metrics(self) -> PerformanceMetrics:
        pass