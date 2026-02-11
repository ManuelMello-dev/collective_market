# Market Dashboard Integration Guide

## Overview

The **Market Intelligence Dashboard** is a brutalist-styled real-time trading UI that integrates with the collective_market microservices architecture. It provides operational intelligence for market monitoring, portfolio tracking, simulation management, and system health monitoring.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Market Dashboard (Node.js)               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  React 19 + Tailwind 4 (Brutalist UI)               │   │
│  │  - Market Monitoring                                │   │
│  │  - Portfolio Performance                            │   │
│  │  - Simulation Engine Status                         │   │
│  │  - Microservices Health                             │   │
│  │  - Alert Management                                 │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  tRPC Backend (Express 4)                           │   │
│  │  - Market data procedures                           │   │
│  │  - Portfolio queries                                │   │
│  │  - Simulation monitoring                            │   │
│  │  - Health checks                                    │   │
│  │  - Alert management                                 │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
    ┌────────┐    ┌────────┐    ┌──────────┐   ┌─────────────┐
    │ Redis  │    │ MySQL  │    │ InfluxDB │   │ ZMQ Bus     │
    │(Episod)│    │(LongTm)│    │(Metrics) │   │(Live Data)  │
    └────────┘    └────────┘    └──────────┘   └─────────────┘
         │              │              │              │
         └──────────────┴──────────────┴──────────────┘
                        │
         ┌──────────────┴──────────────┐
         ▼                             ▼
    ┌─────────────┐            ┌──────────────┐
    │ Ingestion   │            │ Sim Engine   │
    │ Service     │            │ (Z³ State)   │
    └─────────────┘            └──────────────┘
```

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/ManuelMello-dev/collective_market.git
cd collective_market
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` with your settings:

```env
MYSQL_PASSWORD=your_password
INFLUXDB_TOKEN=your_token
JWT_SECRET=your_jwt_secret
POLYGON_API_KEY=your_key
ALPACA_KEY=your_key
ALPACA_SECRET=your_secret
```

### 3. Start Services

```bash
# Start all services (Redis, MySQL, InfluxDB, Prometheus, Grafana, Dashboard)
docker-compose up -d

# View logs
docker-compose logs -f market-dashboard

# Access dashboard
# http://localhost:3000
```

### 4. Verify Integration

```bash
# Check service health
curl http://localhost:3000/health

# Check Redis
redis-cli -p 6379 ping

# Check MySQL
mysql -h localhost -u market -p market_memory

# Check InfluxDB
curl http://localhost:8086/health
```

## Dashboard Pages

### 1. Market Monitoring (`/market`)
- **Live Prices**: Real-time price updates from Redis episodic memory
- **Market Sentiment**: Aggregated sentiment indicators
- **Volume Analysis**: Trading volume visualization
- **Data Source**: Redis (live), MySQL (historical)

### 2. Portfolio Performance (`/portfolio`)
- **Position Management**: Active positions with entry/exit prices
- **P&L Tracking**: Realized and unrealized gains/losses
- **Metrics**: Win rate, Sharpe ratio, maximum drawdown
- **Data Source**: MySQL (positions), InfluxDB (historical metrics)

### 3. Simulation Engine (`/simulation`)
- **Global State (Z³)**: Real-time simulation convergence metric
- **Agent Dynamics**: Individual agent price estimates
- **Active Signals**: Count of agents generating trading signals
- **Metrics**: Convergence rate, volatility, consensus level
- **Data Source**: Redis (live state), MySQL (historical)

### 4. Microservices Health (`/health`)
- **Service Status**: Online/offline status for all microservices
- **Latency Monitoring**: Response times for each service
- **Error Tracking**: Error counts and last error messages
- **Service Controls**: Restart buttons for each service
- **Data Source**: Health check procedures, Prometheus metrics

### 5. Alert Management (`/alerts`)
- **Active Alerts**: Real-time alert notifications
- **Alert Rules**: Circuit breakers, drawdown limits, error thresholds
- **Rule Editor**: Create/edit/delete alert rules
- **Data Source**: MySQL (alert configuration), Redis (active alerts)

## tRPC Procedures

### Market Router
```typescript
// Get latest market prices
trpc.market.getLatestPrices.useQuery()

// Get market sentiment
trpc.market.getMarketSentiment.useQuery()
```

### Portfolio Router
```typescript
// Get portfolio state
trpc.portfolio.getPortfolioState.useQuery()

// Get performance metrics
trpc.portfolio.getPerformanceMetrics.useQuery()
```

### Simulation Router
```typescript
// Get global state (Z³)
trpc.simulation.getGlobalState.useQuery()

// Get active signals
trpc.simulation.getActiveSignals.useQuery()
```

### Health Router
```typescript
// Get system health
trpc.health.getSystemHealth.useQuery()

// Get service status
trpc.health.getServiceStatus.useQuery({ service: 'redis' })
```

### Alerts Router
```typescript
// Get alert rules
trpc.alerts.getAlertRules.useQuery()

// Create alert rule
trpc.alerts.createAlertRule.useMutation()

// Update alert rule
trpc.alerts.updateAlertRule.useMutation()
```

## Integration with Collective Market Services

### Redis Connection
The dashboard connects to Redis to:
- Fetch episodic memory (live market state)
- Subscribe to real-time updates via pub/sub
- Cache frequently accessed data

```typescript
// server/integrations.ts
export async function getRedisClient() {
  return redis.createClient({
    host: process.env.REDIS_HOST || 'localhost',
    port: parseInt(process.env.REDIS_PORT || '6379'),
  });
}
```

### MySQL Connection
The dashboard queries MySQL for:
- Historical market data
- Portfolio positions and trades
- Simulation snapshots
- Alert configuration

```typescript
// Database schema in drizzle/schema.ts
// Tables: market_data, portfolio_positions, simulation_states, alerts_config, etc.
```

### InfluxDB Integration
The dashboard retrieves time-series data for:
- Price history charts
- Portfolio value curves
- Drawdown analysis
- Metric trends

```typescript
// server/integrations.ts
export async function queryInfluxDB(query: string) {
  // Query InfluxDB for time-series data
}
```

### ZMQ Message Bus
The dashboard can subscribe to live updates:
- Market data updates
- Simulation state changes
- Alert triggers

```typescript
// Real-time WebSocket updates to frontend
// (Implementation in progress)
```

## Database Schema

The dashboard extends the collective_market database with:

```sql
-- Market Data (live prices, volumes)
CREATE TABLE market_data (
  id INT PRIMARY KEY AUTO_INCREMENT,
  symbol VARCHAR(10),
  price DECIMAL(10, 2),
  volume BIGINT,
  timestamp DATETIME,
  source VARCHAR(50)
);

-- Portfolio Positions
CREATE TABLE portfolio_positions (
  id INT PRIMARY KEY AUTO_INCREMENT,
  symbol VARCHAR(10),
  quantity DECIMAL(10, 4),
  entry_price DECIMAL(10, 2),
  current_price DECIMAL(10, 2),
  pnl DECIMAL(12, 2),
  status ENUM('open', 'closed')
);

-- Simulation States (Z³ tracking)
CREATE TABLE simulation_states (
  id INT PRIMARY KEY AUTO_INCREMENT,
  step INT,
  global_state DECIMAL(10, 6),
  active_signals INT,
  timestamp DATETIME
);

-- Microservices Health
CREATE TABLE microservices_health (
  id INT PRIMARY KEY AUTO_INCREMENT,
  service_name VARCHAR(50),
  is_healthy BOOLEAN,
  latency_ms DECIMAL(10, 2),
  error_count INT,
  last_error TEXT,
  checked_at DATETIME
);

-- Alert Configuration
CREATE TABLE alerts_config (
  id INT PRIMARY KEY AUTO_INCREMENT,
  rule_name VARCHAR(100),
  rule_type ENUM('circuit_breaker', 'drawdown', 'error_rate', 'latency'),
  threshold DECIMAL(10, 6),
  is_active BOOLEAN,
  created_at DATETIME
);
```

## Deployment

### Docker Compose (Development)
```bash
docker-compose up -d
```

### Kubernetes (Production)
See `kubernetes_deployment.yaml` for production deployment configuration.

### Environment Variables

Create `.env` file with:
```env
# Database
MYSQL_PASSWORD=secure_password
MYSQL_USER=market
MYSQL_DB=market_memory

# InfluxDB
INFLUXDB_TOKEN=secure_token
INFLUXDB_ORG=market-system
INFLUXDB_BUCKET=market-data

# Dashboard
JWT_SECRET=secure_jwt_secret
NODE_ENV=production

# API Keys
POLYGON_API_KEY=your_key
ALPACA_KEY=your_key
ALPACA_SECRET=your_secret
```

## Monitoring

### Access Monitoring Tools

- **Dashboard**: http://localhost:3000
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **InfluxDB**: http://localhost:8086

### Health Checks

```bash
# Dashboard health
curl http://localhost:3000/health

# Redis health
docker-compose exec redis redis-cli ping

# MySQL health
docker-compose exec mysql mysqladmin ping

# InfluxDB health
curl http://localhost:8086/health
```

## Troubleshooting

### Dashboard won't start
```bash
# Check logs
docker-compose logs market-dashboard

# Verify database connection
docker-compose exec market-dashboard node -e "require('mysql2').createConnection({host:'mysql',user:'market',password:'market_pass',database:'market_memory'}).ping(console.log)"
```

### No data appearing
1. Verify Redis/MySQL/InfluxDB are healthy
2. Check that ingestion service is running
3. Verify environment variables are correct
4. Check database tables have data: `SELECT COUNT(*) FROM market_data;`

### Performance issues
1. Check service latencies in Health dashboard
2. Review InfluxDB query performance
3. Check MySQL slow query log
4. Monitor Redis memory usage

## Next Steps

1. **Real-time WebSocket Updates** - Implement live data streaming
2. **Historical Explorer** - Add date-range filtering and export
3. **Replay Mode** - Backtest historical data through sim engine
4. **Position Engine** - Paper/live trading execution
5. **Advanced Analytics** - ML-based signal analysis

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review service logs: `docker-compose logs [service-name]`
3. Open an issue on GitHub with logs and environment details
