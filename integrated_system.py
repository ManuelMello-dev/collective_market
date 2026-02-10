"""
Integrated Market Intelligence System
Combines data publisher, simulation, portfolio management, metrics, and storage
"""
import time
import logging
import argparse
from datetime import datetime
from typing import Dict, List, Optional
import signal
import sys

from portfolio_manager import PortfolioManager
from metrics_exporter import initialize_metrics, get_metrics
from influxdb_writer import InfluxDBWriter

# Import from your existing files (assuming they're available)
# from market_system import (
#     SentimentEngine, EpisodicMemory, LongTermMemory,
#     MarketFetcher, MarketBus, fetch_symbol
# )

logger = logging.getLogger(__name__)


class IntegratedMarketSystem:
    """Fully integrated market intelligence system with all components"""
    
    def __init__(
        self,
        symbols: List[str],
        initial_capital: float = 100000,
        enable_simulation: bool = True,
        enable_portfolio: bool = True,
        enable_metrics: bool = True,
        enable_influxdb: bool = True,
        metrics_port: int = 9090
    ):
        self.symbols = symbols
        self.enable_simulation = enable_simulation
        self.enable_portfolio = enable_portfolio
        self.running = False
        
        logger.info("Initializing Integrated Market System...")
        
        # Initialize metrics exporter
        self.metrics = None
        if enable_metrics:
            try:
                self.metrics = initialize_metrics(port=metrics_port, start_server=True)
                self.metrics.set_system_info({
                    'version': '1.0.0',
                    'environment': 'production',
                    'build_date': datetime.now().isoformat(),
                    'symbols': ','.join(symbols[:10])  # Sample
                })
                logger.info(f"Metrics server started on port {metrics_port}")
            except Exception as e:
                logger.error(f"Failed to start metrics server: {e}")
                self.metrics = None
        
        # Initialize InfluxDB writer
        self.influxdb = None
        if enable_influxdb:
            try:
                self.influxdb = InfluxDBWriter(async_mode=True)
                logger.info("InfluxDB writer initialized")
            except Exception as e:
                logger.error(f"Failed to initialize InfluxDB: {e}")
                self.influxdb = None
        
        # Initialize core components
        # Note: Import from your market_system.py
        # self.sentiment = SentimentEngine()
        # self.episodic = EpisodicMemory()
        # self.archive = LongTermMemory()
        # self.fetcher = MarketFetcher()
        # self.bus = MarketBus()
        
        # Initialize portfolio manager
        self.portfolio = None
        if enable_portfolio:
            self.portfolio = PortfolioManager(
                initial_capital=initial_capital,
                max_position_size=0.1,
                stop_loss_pct=0.05,
                take_profit_pct=0.15,
                max_daily_loss=0.03
            )
            logger.info(f"Portfolio initialized with ${initial_capital:,.2f}")
        
        # Performance tracking
        self.iteration = 0
        self.last_health_check = 0
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    def _health_check_all(self) -> Dict[str, bool]:
        """Perform health checks on all components"""
        health = {}
        
        # Check each component
        # health['sentiment'] = self.sentiment.health_check()
        # health['redis'] = self.episodic.health_check()
        # health['mysql'] = self.archive.health_check()
        # health['fetcher'] = self.fetcher.health_check()
        
        # Update metrics
        if self.metrics:
            for service, is_healthy in health.items():
                self.metrics.set_service_health(service, is_healthy)
        
        return health
    
    def _fetch_market_data(self) -> Dict[str, dict]:
        """Fetch current market data for all symbols"""
        market_data = {}
        
        # Get sentiment
        # sentiment_data = self.sentiment.normalized()
        sentiment_data = {'sentiment_bias': 0.5}  # Placeholder
        
        # Update metrics
        if self.metrics:
            # self.metrics.update_sentiment(...)
            pass
        
        # Fetch data for each symbol
        for symbol in self.symbols:
            start_time = time.time()
            
            try:
                # data = self.fetcher.fetch(symbol)
                # Placeholder data
                data = {
                    'close': 150.0,
                    'volume': 1000000,
                    'sentiment': sentiment_data['sentiment_bias']
                }
                
                if data:
                    market_data[symbol] = data
                    
                    # Record metrics
                    if self.metrics:
                        duration = time.time() - start_time
                        self.metrics.record_data_fetch(
                            'polygon', symbol, duration, True
                        )
                        self.metrics.record_data_publish(symbol)
                    
                    # Write to InfluxDB
                    if self.influxdb:
                        self.influxdb.write_market_data(
                            symbol=symbol,
                            price=data['close'],
                            volume=data['volume'],
                            source='polygon',
                            sentiment=data.get('sentiment')
                        )
                    
                    # Update episodic memory
                    # self.episodic.update(symbol, data)
                    
                    # Publish to bus
                    # self.bus.publish(symbol, data)
                    
            except Exception as e:
                logger.error(f"Error fetching {symbol}: {e}")
                if self.metrics:
                    duration = time.time() - start_time
                    self.metrics.record_data_fetch(
                        'polygon', symbol, duration, False
                    )
                    self.metrics.record_error('fetcher', type(e).__name__)
        
        return market_data
    
    def _process_portfolio_signals(
        self, 
        market_data: Dict[str, dict],
        signals: Optional[Dict[str, str]] = None
    ):
        """Process trading signals through portfolio manager"""
        if not self.portfolio:
            return
        
        # If no signals provided, use simple momentum strategy
        if signals is None:
            signals = {}
            # Simple placeholder strategy
            for symbol in market_data.keys():
                signals[symbol] = 'HOLD'
        
        # Get current prices
        current_prices = {
            sym: data['close'] 
            for sym, data in market_data.items()
        }
        
        # Process signals
        for symbol, signal in signals.items():
            if symbol not in current_prices:
                continue
            
            current_price = current_prices[symbol]
            
            # Process through portfolio manager
            action = self.portfolio.process_signal(
                symbol, signal, current_price
            )
            
            # Record metrics
            if action and self.metrics:
                self.metrics.record_signal(signal)
                if action in ['BUY', 'SELL']:
                    self.metrics.record_trade(action, symbol)
            
            # Write trade to InfluxDB
            if action and self.influxdb and action != 'HOLD':
                position = self.portfolio.positions.get(symbol)
                if action == 'BUY' and position:
                    self.influxdb.write_trade(
                        symbol=symbol,
                        action='BUY',
                        quantity=position.quantity,
                        price=current_price
                    )
                elif action == 'SELL':
                    # Get P&L from last closed trade
                    if self.portfolio.pnl_history:
                        pnl = self.portfolio.pnl_history[-1]
                        self.influxdb.write_trade(
                            symbol=symbol,
                            action='SELL',
                            quantity=0,  # Position already closed
                            price=current_price,
                            pnl=pnl,
                            reason=action
                        )
        
        # Update portfolio state
        portfolio_state = self.portfolio.get_portfolio_state(current_prices)
        
        # Update metrics
        if self.metrics:
            self.metrics.update_portfolio_state(portfolio_state)
        
        # Write to InfluxDB
        if self.influxdb:
            self.influxdb.write_portfolio_state(portfolio_state)
            
            # Write performance metrics
            self.portfolio.calculate_sharpe_ratio()
            self.portfolio.calculate_max_drawdown()
            self.influxdb.write_performance_metrics(
                self.portfolio.metrics
            )
    
    def _run_simulation_step(self, market_data: Dict[str, dict]) -> Dict[str, str]:
        """Run simulation and generate signals"""
        # This would integrate with your simulation code
        # For now, return placeholder signals
        signals = {}
        for symbol in market_data.keys():
            signals[symbol] = 'HOLD'
        
        return signals
    
    def run(self, iterations: Optional[int] = None, interval: float = 1.0):
        """
        Run the integrated system
        
        Args:
            iterations: Number of iterations to run (None = infinite)
            interval: Seconds between iterations
        """
        self.running = True
        iteration = 0
        
        logger.info("Starting integrated market system...")
        logger.info(f"Tracking {len(self.symbols)} symbols")
        logger.info(f"Update interval: {interval}s")
        
        while self.running:
            if iterations and iteration >= iterations:
                break
            
            iteration += 1
            loop_start = time.time()
            
            try:
                # Health checks every 60 seconds
                if time.time() - self.last_health_check > 60:
                    health = self._health_check_all()
                    logger.info(f"Health check: {health}")
                    self.last_health_check = time.time()
                
                # Fetch market data
                market_data = self._fetch_market_data()
                
                if not market_data:
                    logger.warning("No market data fetched")
                    time.sleep(interval)
                    continue
                
                # Run simulation if enabled
                signals = None
                if self.enable_simulation:
                    signals = self._run_simulation_step(market_data)
                    
                    # Update simulation metrics
                    if self.metrics:
                        self.metrics.update_simulation_state(
                            step=iteration,
                            global_state=1000.0  # Placeholder
                        )
                
                # Process portfolio signals
                if self.enable_portfolio:
                    self._process_portfolio_signals(market_data, signals)
                
                # Log progress
                if iteration % 10 == 0:
                    if self.portfolio:
                        state = self.portfolio.get_portfolio_state({
                            sym: data['close'] 
                            for sym, data in market_data.items()
                        })
                        logger.info(
                            f"Iteration {iteration}: "
                            f"Value=${state['total_value']:,.2f} "
                            f"P&L=${state['total_pnl']:+,.2f} "
                            f"Positions={state['positions_count']}"
                        )
                    else:
                        logger.info(f"Iteration {iteration}: Processed {len(market_data)} symbols")
                
                # Sleep to maintain interval
                elapsed = time.time() - loop_start
                sleep_time = max(0, interval - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                if self.metrics:
                    self.metrics.record_error('main_loop', type(e).__name__)
                time.sleep(5)  # Backoff on error
        
        self.shutdown()
    
    def shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down integrated market system...")
        
        # Print final portfolio state
        if self.portfolio:
            current_prices = {}  # Would get from last market data
            summary = self.portfolio.get_performance_summary(current_prices)
            
            logger.info("=" * 80)
            logger.info("FINAL PORTFOLIO SUMMARY")
            logger.info("=" * 80)
            logger.info(f"Initial Capital: ${self.portfolio.initial_capital:,.2f}")
            logger.info(f"Final Value: ${summary['total_value']:,.2f}")
            logger.info(f"Total P&L: ${summary['total_pnl']:+,.2f} ({summary['return_pct']:+.2f}%)")
            logger.info(f"Closed P&L: ${summary['closed_pnl']:+,.2f}")
            logger.info(f"Unrealized P&L: ${summary['unrealized_pnl']:+,.2f}")
            logger.info("")
            logger.info(f"Total Trades: {summary['performance']['total_trades']}")
            logger.info(f"Win Rate: {summary['performance']['win_rate']:.1%}")
            logger.info(f"Sharpe Ratio: {summary['performance']['sharpe_ratio']:.2f}")
            logger.info(f"Max Drawdown: {summary['performance']['max_drawdown']:.2%}")
            logger.info("=" * 80)
        
        # Close connections
        if self.influxdb:
            self.influxdb.close()
        
        logger.info("Shutdown complete")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Integrated Market Intelligence System")
    parser.add_argument(
        '--symbols',
        type=str,
        default='AAPL,MSFT,GOOGL,AMZN,NVDA',
        help='Comma-separated symbols'
    )
    parser.add_argument(
        '--capital',
        type=float,
        default=100000,
        help='Initial capital'
    )
    parser.add_argument(
        '--iterations',
        type=int,
        default=None,
        help='Number of iterations (None=infinite)'
    )
    parser.add_argument(
        '--interval',
        type=float,
        default=1.0,
        help='Update interval in seconds'
    )
    parser.add_argument(
        '--no-simulation',
        action='store_true',
        help='Disable simulation'
    )
    parser.add_argument(
        '--no-portfolio',
        action='store_true',
        help='Disable portfolio tracking'
    )
    parser.add_argument(
        '--no-metrics',
        action='store_true',
        help='Disable Prometheus metrics'
    )
    parser.add_argument(
        '--no-influxdb',
        action='store_true',
        help='Disable InfluxDB storage'
    )
    parser.add_argument(
        '--metrics-port',
        type=int,
        default=9090,
        help='Prometheus metrics port'
    )
    
    args = parser.parse_args()
    symbols = args.symbols.split(',')
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run system
    system = IntegratedMarketSystem(
        symbols=symbols,
        initial_capital=args.capital,
        enable_simulation=not args.no_simulation,
        enable_portfolio=not args.no_portfolio,
        enable_metrics=not args.no_metrics,
        enable_influxdb=not args.no_influxdb,
        metrics_port=args.metrics_port
    )
    
    system.run(iterations=args.iterations, interval=args.interval)


if __name__ == "__main__":
    main()

