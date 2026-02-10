"""
Prometheus Metrics Exporter for Market System
Exposes system health, performance, and trading metrics
"""
import time
from prometheus_client import (
    Counter, Gauge, Histogram, Summary, Info,
    start_http_server, REGISTRY
)
import logging
from typing import Dict, Optional
from dataclasses import dataclass
import threading

logger = logging.getLogger(__name__)


class MetricsExporter:
    """Centralized metrics collection and export for Prometheus"""
    
    def __init__(self, port: int = 9090):
        self.port = port
        self._init_metrics()
        logger.info(f"Metrics exporter initialized on port {port}")
    
    def _init_metrics(self):
        """Initialize all Prometheus metrics"""
        
        # System Health Metrics
        self.service_up = Gauge(
            'market_system_service_up',
            'Service health status (1=up, 0=down)',
            ['service']
        )
        
        self.circuit_breaker_state = Gauge(
            'market_system_circuit_breaker_state',
            'Circuit breaker state (0=closed, 1=open, 2=half-open)',
            ['service']
        )
        
        # Data Pipeline Metrics
        self.data_fetch_total = Counter(
            'market_system_data_fetch_total',
            'Total data fetch attempts',
            ['source', 'symbol', 'status']
        )
        
        self.data_fetch_duration = Histogram(
            'market_system_data_fetch_duration_seconds',
            'Data fetch duration',
            ['source', 'symbol'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
        )
        
        self.data_points_published = Counter(
            'market_system_data_points_published_total',
            'Total data points published to message bus',
            ['symbol']
        )
        
        # Sentiment Metrics
        self.sentiment_value = Gauge(
            'market_system_sentiment_value',
            'Current sentiment value (0-100)',
            ['type']  # equity or crypto
        )
        
        self.sentiment_normalized = Gauge(
            'market_system_sentiment_normalized',
            'Normalized sentiment value (0-1)',
            ['type']
        )
        
        # Memory System Metrics
        self.redis_operations = Counter(
            'market_system_redis_operations_total',
            'Redis operations',
            ['operation', 'status']
        )
        
        self.redis_latency = Histogram(
            'market_system_redis_latency_seconds',
            'Redis operation latency',
            ['operation'],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5]
        )
        
        self.mysql_operations = Counter(
            'market_system_mysql_operations_total',
            'MySQL operations',
            ['operation', 'status']
        )
        
        self.mysql_latency = Histogram(
            'market_system_mysql_latency_seconds',
            'MySQL operation latency',
            ['operation'],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
        )
        
        # Portfolio Metrics
        self.portfolio_value = Gauge(
            'market_system_portfolio_value_dollars',
            'Current portfolio value in dollars'
        )
        
        self.portfolio_pnl = Gauge(
            'market_system_portfolio_pnl_dollars',
            'Portfolio profit/loss in dollars',
            ['type']  # realized or unrealized
        )
        
        self.portfolio_positions = Gauge(
            'market_system_portfolio_positions_count',
            'Number of open positions'
        )
        
        self.trades_total = Counter(
            'market_system_trades_total',
            'Total trades executed',
            ['action', 'symbol']
        )
        
        self.trade_pnl = Histogram(
            'market_system_trade_pnl_dollars',
            'Individual trade P&L distribution',
            buckets=[-1000, -500, -100, 0, 100, 500, 1000, 5000, 10000]
        )
        
        self.win_rate = Gauge(
            'market_system_win_rate',
            'Trading win rate (0-1)'
        )
        
        # Simulation Metrics
        self.simulation_step = Gauge(
            'market_system_simulation_step',
            'Current simulation step'
        )
        
        self.simulation_global_state = Gauge(
            'market_system_simulation_global_state',
            'Global simulation state (Z³ value)'
        )
        
        self.agent_prices = Gauge(
            'market_system_agent_price',
            'Individual agent price',
            ['security_id']
        )
        
        self.simulation_signals = Counter(
            'market_system_simulation_signals_total',
            'Trading signals generated',
            ['signal_type']  # BUY, SELL, HOLD
        )
        
        # Message Bus Metrics
        self.zmq_messages_sent = Counter(
            'market_system_zmq_messages_sent_total',
            'ZMQ messages sent',
            ['topic']
        )
        
        self.zmq_latency = Histogram(
            'market_system_zmq_publish_latency_seconds',
            'ZMQ publish latency',
            buckets=[0.0001, 0.001, 0.01, 0.1]
        )
        
        # Error Metrics
        self.errors_total = Counter(
            'market_system_errors_total',
            'Total errors',
            ['component', 'error_type']
        )
        
        # System Info
        self.system_info = Info(
            'market_system_build_info',
            'System build information'
        )
    
    def start_server(self):
        """Start Prometheus HTTP server"""
        try:
            start_http_server(self.port)
            logger.info(f"Metrics server started on port {self.port}")
        except OSError as e:
            logger.error(f"Failed to start metrics server: {e}")
            raise
    
    # Health Metrics
    def set_service_health(self, service: str, is_healthy: bool):
        """Set service health status"""
        self.service_up.labels(service=service).set(1 if is_healthy else 0)
    
    def set_circuit_breaker_state(self, service: str, state: str):
        """Set circuit breaker state (CLOSED=0, OPEN=1, HALF_OPEN=2)"""
        state_map = {'CLOSED': 0, 'OPEN': 1, 'HALF_OPEN': 2}
        self.circuit_breaker_state.labels(service=service).set(
            state_map.get(state, 0)
        )
    
    # Data Pipeline Metrics
    def record_data_fetch(
        self, 
        source: str, 
        symbol: str, 
        duration: float, 
        success: bool
    ):
        """Record data fetch metrics"""
        status = 'success' if success else 'failure'
        self.data_fetch_total.labels(
            source=source, 
            symbol=symbol, 
            status=status
        ).inc()
        self.data_fetch_duration.labels(
            source=source, 
            symbol=symbol
        ).observe(duration)
    
    def record_data_publish(self, symbol: str):
        """Record data point published"""
        self.data_points_published.labels(symbol=symbol).inc()
    
    # Sentiment Metrics
    def update_sentiment(
        self, 
        equity_fg: float, 
        crypto_fg: float,
        equity_norm: float,
        crypto_norm: float
    ):
        """Update sentiment metrics"""
        self.sentiment_value.labels(type='equity').set(equity_fg)
        self.sentiment_value.labels(type='crypto').set(crypto_fg)
        self.sentiment_normalized.labels(type='equity').set(equity_norm)
        self.sentiment_normalized.labels(type='crypto').set(crypto_norm)
    
    # Memory Metrics
    def record_redis_op(self, operation: str, duration: float, success: bool):
        """Record Redis operation"""
        status = 'success' if success else 'failure'
        self.redis_operations.labels(
            operation=operation, 
            status=status
        ).inc()
        self.redis_latency.labels(operation=operation).observe(duration)
    
    def record_mysql_op(self, operation: str, duration: float, success: bool):
        """Record MySQL operation"""
        status = 'success' if success else 'failure'
        self.mysql_operations.labels(
            operation=operation, 
            status=status
        ).inc()
        self.mysql_latency.labels(operation=operation).observe(duration)
    
    # Portfolio Metrics
    def update_portfolio_state(self, portfolio_state: dict):
        """Update portfolio metrics from portfolio state"""
        self.portfolio_value.set(portfolio_state.get('total_value', 0))
        self.portfolio_pnl.labels(type='realized').set(
            portfolio_state.get('closed_pnl', 0)
        )
        self.portfolio_pnl.labels(type='unrealized').set(
            portfolio_state.get('unrealized_pnl', 0)
        )
        self.portfolio_positions.set(
            portfolio_state.get('positions_count', 0)
        )
        
        metrics = portfolio_state.get('metrics', {})
        self.win_rate.set(metrics.get('win_rate', 0))
    
    def record_trade(self, action: str, symbol: str, pnl: Optional[float] = None):
        """Record trade execution"""
        self.trades_total.labels(action=action, symbol=symbol).inc()
        if pnl is not None:
            self.trade_pnl.observe(pnl)
    
    # Simulation Metrics
    def update_simulation_state(
        self, 
        step: int, 
        global_state: float,
        agent_prices: Optional[Dict[str, float]] = None
    ):
        """Update simulation metrics"""
        self.simulation_step.set(step)
        self.simulation_global_state.set(global_state)
        
        if agent_prices:
            for security_id, price in agent_prices.items():
                self.agent_prices.labels(security_id=security_id).set(price)
    
    def record_signal(self, signal_type: str):
        """Record trading signal generation"""
        self.simulation_signals.labels(signal_type=signal_type).inc()
    
    # Message Bus Metrics
    def record_zmq_message(self, topic: str, duration: float):
        """Record ZMQ message sent"""
        self.zmq_messages_sent.labels(topic=topic).inc()
        self.zmq_latency.observe(duration)
    
    # Error Metrics
    def record_error(self, component: str, error_type: str):
        """Record error occurrence"""
        self.errors_total.labels(
            component=component, 
            error_type=error_type
        ).inc()
    
    # System Info
    def set_system_info(self, info: dict):
        """Set system build information"""
        self.system_info.info(info)


# Global metrics instance
_metrics_instance: Optional[MetricsExporter] = None
_metrics_lock = threading.Lock()


def get_metrics() -> MetricsExporter:
    """Get or create global metrics exporter instance"""
    global _metrics_instance
    
    if _metrics_instance is None:
        with _metrics_lock:
            if _metrics_instance is None:
                _metrics_instance = MetricsExporter()
    
    return _metrics_instance


def initialize_metrics(port: int = 9090, start_server: bool = True) -> MetricsExporter:
    """Initialize metrics exporter and optionally start HTTP server"""
    global _metrics_instance
    
    with _metrics_lock:
        _metrics_instance = MetricsExporter(port=port)
        if start_server:
            _metrics_instance.start_server()
    
    return _metrics_instance


# Decorator for timing operations
def timed_operation(component: str, operation: str):
    """Decorator to time and record operation metrics"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            metrics = get_metrics()
            start_time = time.time()
            success = False
            
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                metrics.record_error(component, type(e).__name__)
                raise
            finally:
                duration = time.time() - start_time
                
                # Record based on component
                if 'redis' in component.lower():
                    metrics.record_redis_op(operation, duration, success)
                elif 'mysql' in component.lower():
                    metrics.record_mysql_op(operation, duration, success)
        
        return wrapper
    return decorator


# Example usage
if __name__ == "__main__":
    import random
    
    # Initialize metrics with server
    metrics = initialize_metrics(port=9090, start_server=True)
    
    # Set system info
    metrics.set_system_info({
        'version': '1.0.0',
        'environment': 'production',
        'build_date': '2026-02-10'
    })
    
    # Simulate some metrics
    print("Metrics server running on http://localhost:9090/metrics")
    print("Simulating metrics for 60 seconds...")
    
    for i in range(60):
        # Health checks
        metrics.set_service_health('redis', True)
        metrics.set_service_health('mysql', random.choice([True, False]))
        
        # Data fetches
        for symbol in ['AAPL', 'MSFT', 'GOOGL']:
            duration = random.uniform(0.1, 2.0)
            success = random.random() > 0.1
            metrics.record_data_fetch('polygon', symbol, duration, success)
            if success:
                metrics.record_data_publish(symbol)
        
        # Sentiment
        metrics.update_sentiment(
            equity_fg=random.uniform(20, 80),
            crypto_fg=random.uniform(20, 80),
            equity_norm=random.uniform(0.2, 0.8),
            crypto_norm=random.uniform(0.2, 0.8)
        )
        
        # Portfolio
        portfolio_state = {
            'total_value': 100000 + random.uniform(-5000, 10000),
            'closed_pnl': random.uniform(-1000, 5000),
            'unrealized_pnl': random.uniform(-500, 1000),
            'positions_count': random.randint(0, 10),
            'metrics': {'win_rate': random.uniform(0.4, 0.7)}
        }
        metrics.update_portfolio_state(portfolio_state)
        
        # Trades
        if random.random() > 0.7:
            action = random.choice(['BUY', 'SELL'])
            symbol = random.choice(['AAPL', 'MSFT'])
            pnl = random.uniform(-100, 200) if action == 'SELL' else None
            metrics.record_trade(action, symbol, pnl)
        
        # Simulation
        metrics.update_simulation_state(
            step=i,
            global_state=1000 + random.uniform(-50, 50)
        )
        
        time.sleep(1)
    
    print("Simulation complete. Server will continue running...")
    print("Press Ctrl+C to stop")
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
