"""
InfluxDB Time-Series Storage Integration
Stores market data, simulation states, and portfolio metrics for analysis
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import os
from influxdb_client import InfluxDBClient, Point, WritePrecision, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS, ASYNCHRONOUS
import threading
import queue

logger = logging.getLogger(__name__)


class InfluxDBWriter:
    """High-performance time-series data writer for InfluxDB"""
    
    def __init__(
        self,
        url: Optional[str] = None,
        token: Optional[str] = None,
        org: Optional[str] = None,
        bucket: Optional[str] = None,
        batch_size: int = 1000,
        flush_interval: int = 10000,  # milliseconds
        async_mode: bool = True
    ):
        """
        Initialize InfluxDB writer
        
        Args:
            url: InfluxDB URL (default from INFLUXDB_URL env var)
            token: Auth token (default from INFLUXDB_TOKEN env var)
            org: Organization (default from INFLUXDB_ORG env var)
            bucket: Bucket name (default from INFLUXDB_BUCKET env var)
            batch_size: Points per batch for async writes
            flush_interval: Flush interval in ms
            async_mode: Use async writes for better performance
        """
        self.url = url or os.getenv('INFLUXDB_URL', 'http://localhost:8086')
        self.token = token or os.getenv('INFLUXDB_TOKEN')
        self.org = org or os.getenv('INFLUXDB_ORG', 'market-system')
        self.bucket = bucket or os.getenv('INFLUXDB_BUCKET', 'market-data')
        
        if not self.token:
            raise ValueError("InfluxDB token not provided")
        
        # Initialize client
        self.client = InfluxDBClient(
            url=self.url,
            token=self.token,
            org=self.org
        )
        
        # Initialize write API
        if async_mode:
            write_options = WriteOptions(
                batch_size=batch_size,
                flush_interval=flush_interval,
                jitter_interval=2000,
                retry_interval=5000,
                max_retries=3
            )
            self.write_api = self.client.write_api(write_options=write_options)
        else:
            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        
        self.query_api = self.client.query_api()
        
        logger.info(
            f"InfluxDB client initialized: {self.url} | "
            f"Org: {self.org} | Bucket: {self.bucket} | "
            f"Mode: {'async' if async_mode else 'sync'}"
        )
    
    def write_market_data(
        self,
        symbol: str,
        price: float,
        volume: float,
        source: str,
        sentiment: Optional[float] = None,
        timestamp: Optional[datetime] = None
    ):
        """Write market data point"""
        timestamp = timestamp or datetime.utcnow()
        
        point = (
            Point("market_data")
            .tag("symbol", symbol)
            .tag("source", source)
            .field("price", price)
            .field("volume", volume)
            .time(timestamp, WritePrecision.NS)
        )
        
        if sentiment is not None:
            point.field("sentiment", sentiment)
        
        self._write_point(point)
    
    def write_sentiment(
        self,
        equity_fg: float,
        crypto_fg: float,
        equity_label: str,
        crypto_label: str,
        timestamp: Optional[datetime] = None
    ):
        """Write sentiment indicators"""
        timestamp = timestamp or datetime.utcnow()
        
        point = (
            Point("sentiment")
            .tag("equity_label", equity_label)
            .tag("crypto_label", crypto_label)
            .field("equity_fg", equity_fg)
            .field("crypto_fg", crypto_fg)
            .field("equity_fg_norm", equity_fg / 100.0)
            .field("crypto_fg_norm", crypto_fg / 100.0)
            .field("sentiment_bias", (equity_fg * 0.6 + crypto_fg * 0.4) / 100.0)
            .time(timestamp, WritePrecision.NS)
        )
        
        self._write_point(point)
    
    def write_portfolio_state(
        self,
        portfolio_state: dict,
        timestamp: Optional[datetime] = None
    ):
        """Write portfolio state snapshot"""
        timestamp = timestamp or datetime.utcnow()
        
        # Main portfolio point
        point = (
            Point("portfolio")
            .field("capital", portfolio_state.get('capital', 0))
            .field("total_value", portfolio_state.get('total_value', 0))
            .field("closed_pnl", portfolio_state.get('closed_pnl', 0))
            .field("unrealized_pnl", portfolio_state.get('unrealized_pnl', 0))
            .field("total_pnl", portfolio_state.get('total_pnl', 0))
            .field("return_pct", portfolio_state.get('return_pct', 0))
            .field("positions_count", portfolio_state.get('positions_count', 0))
            .time(timestamp, WritePrecision.NS)
        )
        
        self._write_point(point)
        
        # Individual positions
        positions = portfolio_state.get('positions', {})
        for symbol, pos_data in positions.items():
            pos_point = (
                Point("position")
                .tag("symbol", symbol)
                .field("quantity", pos_data.get('quantity', 0))
                .field("entry_price", pos_data.get('entry_price', 0))
                .field("current_price", pos_data.get('current_price', 0))
                .field("unrealized_pnl", pos_data.get('unrealized_pnl', 0))
                .field("pnl_pct", pos_data.get('pnl_pct', 0))
                .time(timestamp, WritePrecision.NS)
            )
            self._write_point(pos_point)
    
    def write_trade(
        self,
        symbol: str,
        action: str,
        quantity: float,
        price: float,
        pnl: Optional[float] = None,
        reason: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ):
        """Write trade execution"""
        timestamp = timestamp or datetime.utcnow()
        
        point = (
            Point("trade")
            .tag("symbol", symbol)
            .tag("action", action)
            .field("quantity", quantity)
            .field("price", price)
            .field("value", quantity * price)
            .time(timestamp, WritePrecision.NS)
        )
        
        if pnl is not None:
            point.field("pnl", pnl)
        if reason:
            point.tag("reason", reason)
        
        self._write_point(point)
    
    def write_simulation_state(
        self,
        step: int,
        global_state: float,
        agent_prices: Optional[Dict[str, float]] = None,
        signals: Optional[Dict[str, str]] = None,
        timestamp: Optional[datetime] = None
    ):
        """Write simulation state"""
        timestamp = timestamp or datetime.utcnow()
        
        # Global simulation state
        point = (
            Point("simulation")
            .field("step", step)
            .field("global_state", global_state)
            .time(timestamp, WritePrecision.NS)
        )
        
        self._write_point(point)
        
        # Individual agent states (sample to avoid overwhelming)
        if agent_prices:
            # Write only top N agents or sample
            for security_id, price in list(agent_prices.items())[:100]:
                agent_point = (
                    Point("agent_price")
                    .tag("security_id", security_id)
                    .field("price", price)
                    .time(timestamp, WritePrecision.NS)
                )
                
                if signals and security_id in signals:
                    agent_point.tag("signal", signals[security_id])
                
                self._write_point(agent_point)
    
    def write_performance_metrics(
        self,
        metrics: dict,
        timestamp: Optional[datetime] = None
    ):
        """Write performance metrics"""
        timestamp = timestamp or datetime.utcnow()
        
        point = (
            Point("performance")
            .field("sharpe_ratio", metrics.get('sharpe_ratio', 0))
            .field("max_drawdown", metrics.get('max_drawdown', 0))
            .field("win_rate", metrics.get('win_rate', 0))
            .field("total_trades", metrics.get('total_trades', 0))
            .field("winning_trades", metrics.get('winning_trades', 0))
            .field("losing_trades", metrics.get('losing_trades', 0))
            .field("total_pnl", metrics.get('total_pnl', 0))
            .time(timestamp, WritePrecision.NS)
        )
        
        self._write_point(point)
    
    def write_system_health(
        self,
        component: str,
        is_healthy: bool,
        latency_ms: Optional[float] = None,
        error_count: int = 0,
        timestamp: Optional[datetime] = None
    ):
        """Write system health metrics"""
        timestamp = timestamp or datetime.utcnow()
        
        point = (
            Point("system_health")
            .tag("component", component)
            .field("is_healthy", 1 if is_healthy else 0)
            .field("error_count", error_count)
            .time(timestamp, WritePrecision.NS)
        )
        
        if latency_ms is not None:
            point.field("latency_ms", latency_ms)
        
        self._write_point(point)
    
    def _write_point(self, point: Point):
        """Internal method to write a point"""
        try:
            self.write_api.write(
                bucket=self.bucket,
                org=self.org,
                record=point
            )
        except Exception as e:
            logger.error(f"Failed to write point to InfluxDB: {e}")
    
    def query_recent_prices(
        self,
        symbol: str,
        window: str = "1h"
    ) -> List[Dict[str, Any]]:
        """Query recent prices for a symbol"""
        query = f'''
        from(bucket: "{self.bucket}")
            |> range(start: -{window})
            |> filter(fn: (r) => r["_measurement"] == "market_data")
            |> filter(fn: (r) => r["symbol"] == "{symbol}")
            |> filter(fn: (r) => r["_field"] == "price")
        '''
        
        try:
            result = self.query_api.query(query=query)
            records = []
            for table in result:
                for record in table.records:
                    records.append({
                        'time': record.get_time(),
                        'price': record.get_value(),
                        'source': record.values.get('source')
                    })
            return records
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return []
    
    def query_portfolio_performance(
        self,
        window: str = "24h"
    ) -> Dict[str, Any]:
        """Query portfolio performance over time window"""
        query = f'''
        from(bucket: "{self.bucket}")
            |> range(start: -{window})
            |> filter(fn: (r) => r["_measurement"] == "portfolio")
            |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        '''
        
        try:
            result = self.query_api.query(query=query)
            records = []
            for table in result:
                for record in table.records:
                    records.append(record.values)
            
            if not records:
                return {}
            
            # Calculate statistics
            latest = records[-1]
            initial = records[0]
            
            return {
                'latest_value': latest.get('total_value', 0),
                'initial_value': initial.get('total_value', 0),
                'change_pct': (
                    (latest.get('total_value', 0) - initial.get('total_value', 0)) /
                    initial.get('total_value', 1) * 100
                ),
                'peak_value': max(r.get('total_value', 0) for r in records),
                'lowest_value': min(r.get('total_value', 0) for r in records),
                'total_pnl': latest.get('total_pnl', 0),
            }
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return {}
    
    def close(self):
        """Close client and flush remaining writes"""
        try:
            self.write_api.close()
            self.client.close()
            logger.info("InfluxDB client closed")
        except Exception as e:
            logger.error(f"Error closing InfluxDB client: {e}")
    
    def __del__(self):
        """Cleanup on deletion"""
        self.close()


# Example usage
if __name__ == "__main__":
    import time
    import random
    
    logging.basicConfig(level=logging.INFO)
    
    # Initialize writer
    # Note: You need to set INFLUXDB_TOKEN environment variable
    # or pass token explicitly
    try:
        writer = InfluxDBWriter(
            url="http://localhost:8086",
            token=os.getenv('INFLUXDB_TOKEN', 'my-token'),
            org="market-system",
            bucket="market-data",
            async_mode=True
        )
        
        print("Writing sample data to InfluxDB...")
        
        # Write market data
        for i in range(10):
            writer.write_market_data(
                symbol='AAPL',
                price=150.0 + random.uniform(-5, 5),
                volume=1000000 + random.randint(-100000, 100000),
                source='polygon',
                sentiment=random.uniform(-1, 1)
            )
            
            # Write sentiment
            writer.write_sentiment(
                equity_fg=random.uniform(20, 80),
                crypto_fg=random.uniform(20, 80),
                equity_label='Neutral',
                crypto_label='Fear'
            )
            
            # Write portfolio state
            portfolio_state = {
                'capital': 50000,
                'total_value': 100000 + random.uniform(-5000, 5000),
                'closed_pnl': random.uniform(-1000, 2000),
                'unrealized_pnl': random.uniform(-500, 1000),
                'total_pnl': random.uniform(-500, 3000),
                'return_pct': random.uniform(-5, 15),
                'positions_count': random.randint(3, 8)
            }
            writer.write_portfolio_state(portfolio_state)
            
            time.sleep(0.5)
        
        # Wait for async writes to complete
        time.sleep(2)
        
        # Query recent data
        print("\nQuerying recent AAPL prices...")
        recent_prices = writer.query_recent_prices('AAPL', window='1h')
        for record in recent_prices[-5:]:
            print(f"  {record['time']}: ${record['price']:.2f}")
        
        # Query performance
        print("\nQuerying portfolio performance...")
        performance = writer.query_portfolio_performance(window='1h')
        print(f"  Latest Value: ${performance.get('latest_value', 0):,.2f}")
        print(f"  Change: {performance.get('change_pct', 0):+.2f}%")
        print(f"  Total P&L: ${performance.get('total_pnl', 0):+,.2f}")
        
        writer.close()
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure InfluxDB is running and INFLUXDB_TOKEN is set:")
        print("  docker run -p 8086:8086 influxdb:latest")
        print("  export INFLUXDB_TOKEN='your-token'")
