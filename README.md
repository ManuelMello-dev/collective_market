Market Intelligence System - Production Deployment Guide
📋 Table of Contents
Architecture Overview
Quick Start
Local Development
Production Deployment
Monitoring & Observability
Configuration
Troubleshooting
🏗️ Architecture Overview
System Components
┌─────────────────────────────────────────────────────────────┐
│                    Market Intelligence System                 │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐      ┌───────────┐  │
│  │   Sentiment  │      │    Market    │      │ Simulation│  │
│  │    Engine    │─────▶│   Fetcher    │─────▶│  Engine   │  │
│  │  (F&G Index) │      │ (Multi-src)  │      │ (PyTorch) │  │
│  └──────────────┘      └──────────────┘      └───────────┘  │
│         │                      │                     │        │
│         │                      ▼                     │        │
│         │              ┌──────────────┐              │        │
│         │              │   ZeroMQ     │              │        │
│         │              │  Message Bus │              │        │
│         │              └──────────────┘              │        │
│         │                      │                     │        │
│         ▼                      ▼                     ▼        │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              Portfolio Manager (Risk Control)          │  │
│  └────────────────────────────────────────────────────────┘  │
│         │                      │                     │        │
│         ▼                      ▼                     ▼        │
│  ┌──────────┐         ┌───────────┐         ┌──────────┐    │
│  │  Redis   │         │  MySQL    │         │ InfluxDB │    │
│  │(Episodic)│         │(Long-term)│         │(Metrics) │    │
│  └──────────┘         └───────────┘         └──────────┘    │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │    Prometheus Metrics    │    Grafana Dashboards       │  │
│  └────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
Data Flow
Market Data Collection: Multi-source fetching (yfinance → Polygon → Alpaca → CCXT)
Sentiment Analysis: Fear & Greed indices for equity + crypto markets
Memory Systems:
Redis (episodic, 1-hour TTL)
MySQL (long-term archival)
Agent Simulation: PyTorch-based multi-agent market dynamics
Portfolio Management: Risk-controlled position tracking with stop-loss/take-profit
Observability: Prometheus metrics + InfluxDB time-series + Grafana visualization
🚀 Quick Start
Prerequisites
# System requirements
- Python 3.9+
- Docker & Docker Compose
- kubectl (for Kubernetes deployment)
- 4GB+ RAM
- Optional: NVIDIA GPU for simulation acceleration
1. Local Docker Compose Setup
# Clone repository
git clone <your-repo>
cd market-intelligence-system

# Create .env file
cat > .env << EOF
POLYGON_API_KEY=your_key_here
ALPACA_KEY=your_key_here
ALPACA_SECRET=your_secret_here
MYSQL_PASSWORD=secure_password
INFLUXDB_TOKEN=your_influx_token
EOF

# Start infrastructure
docker-compose up -d redis mysql influxdb prometheus grafana

# Verify services
docker-compose ps
2. Install Python Dependencies
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt
3. Run the System
# Run integrated system
python integrated_system.py \
    --symbols AAPL,MSFT,GOOGL,AMZN,NVDA \
    --capital 100000 \
    --interval 1.0

# Or run components separately:

# Terminal 1: Market data publisher
python market_system.py --symbols AAPL,MSFT,GOOGL

# Terminal 2: Simulation engine
python simulation.py
4. Access Dashboards
Grafana: http://localhost:3000 (admin/admin)
Prometheus: http://localhost:9090
Metrics: http://localhost:9090/metrics
InfluxDB: http://localhost:8086
💻 Local Development
Running Individual Components
Portfolio Manager
from portfolio_manager import PortfolioManager

portfolio = PortfolioManager(
    initial_capital=100000,
    max_position_size=0.1,
    stop_loss_pct=0.05
)

# Process signals
portfolio.process_signal('AAPL', 'BUY', 150.0)
portfolio.process_signal('AAPL', 'SELL', 160.0)

# Get state
state = portfolio.get_portfolio_state({'AAPL': 160.0})
print(f"Total P&L: ${state['total_pnl']:,.2f}")
Metrics Export
from metrics_exporter import initialize_metrics, get_metrics

# Initialize
metrics = initialize_metrics(port=9090)

# Record metrics
metrics.set_service_health('redis', True)
metrics.record_data_fetch('polygon', 'AAPL', 0.5, True)
metrics.record_trade('BUY', 'AAPL', pnl=250.0)

# Access at http://localhost:9090/metrics
InfluxDB Storage
from influxdb_writer import InfluxDBWriter

writer = InfluxDBWriter()

# Write market data
writer.write_market_data(
    symbol='AAPL',
    price=150.0,
    volume=1000000,
    source='polygon'
)

# Query data
recent = writer.query_recent_prices('AAPL', window='1h')
Testing
# Run unit tests
pytest tests/ -v

# Run integration tests
pytest tests/integration/ -v

# Run with coverage
pytest --cov=. --cov-report=html

## 🚂 Production Deployment (Railway)

Railway is a modern platform-as-a-service that simplifies deployment. The system can be deployed as two separate services:

1. **Web Service**: FastAPI application for health checks and API endpoints
2. **Worker Service**: Long-running market intelligence system

### Prerequisites

- Railway account (https://railway.app)
- GitHub repository connected to Railway
- Python version pinned to 3.11.x (Railway uses `.python-version` and `runtime.txt`)

### Why Python 3.11?

Python 3.13.x has compatibility issues with `numpy==1.24.3` during pip install, causing `BackendUnavailable: Cannot import 'setuptools.build_meta'` errors. Python 3.11.x is stable and fully compatible with all dependencies.

### 1. Setup Managed Services

Railway provides managed databases. Create these services in your Railway project:

- **Redis**: For episodic memory (1-hour TTL cache)
- **MySQL**: For long-term data archival
- **InfluxDB** (optional): For time-series metrics (or use external service)

### 2. Configure Environment Variables

Set these environment variables in Railway for both services:

#### Database Configuration
```bash
# Redis (from Railway Redis service)
REDIS_URL=redis://default:password@redis.railway.internal:6379
# Or individual components:
REDIS_HOST=redis.railway.internal
REDIS_PORT=6379

# MySQL (from Railway MySQL service)
MYSQL_HOST=mysql.railway.internal
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=market_memory
MYSQL_DB=market_memory

# InfluxDB (external or Railway deployment)
INFLUXDB_URL=http://influxdb.railway.internal:8086
INFLUXDB_TOKEN=your_influxdb_token
INFLUXDB_ORG=market-system
INFLUXDB_BUCKET=market-data
```

#### API Keys
```bash
POLYGON_API_KEY=your_polygon_key
ALPACA_KEY=your_alpaca_key
ALPACA_SECRET=your_alpaca_secret
```

#### Service Configuration
```bash
# Metrics port (for worker service)
METRICS_PORT=9090

# ZMQ port (for internal messaging)
ZMQ_PORT=5555
```

### 3. Deploy Web Service

Create a new service in Railway:

**Service Name**: `market-web`

**Build Configuration**:
- Builder: Nixpacks (automatic)
- Python version: Detected from `.python-version` and `runtime.txt`

**Start Command**:
```bash
uvicorn web:app --host 0.0.0.0 --port $PORT
```

**Health Check Path**: `/health`

**Endpoints**:
- `GET /health` - Health check for load balancers
- `GET /status` - Detailed runtime status and configuration
- `GET /metrics` - Prometheus metrics (if worker is running)
- `GET /ready` - Readiness probe
- `GET /live` - Liveness probe

**Port**: Railway automatically sets `$PORT` environment variable

### 4. Deploy Worker Service

Create a second service in Railway:

**Service Name**: `market-worker`

**Build Configuration**:
- Builder: Nixpacks (automatic)
- Python version: Detected from `.python-version` and `runtime.txt`

**Start Command**:
```bash
python integrated_system.py --symbols AAPL,MSFT,GOOGL,AMZN,NVDA --capital 100000 --interval 1.0
```

**Customize Parameters**:
- `--symbols`: Comma-separated stock symbols to track
- `--capital`: Initial capital for portfolio
- `--interval`: Update interval in seconds
- `--no-simulation`: Disable simulation engine
- `--no-portfolio`: Disable portfolio tracking
- `--no-metrics`: Disable Prometheus metrics
- `--metrics-port`: Port for metrics server (default: 9090)

**Example Alternative Commands**:
```bash
# Minimal worker (no metrics, no simulation)
python integrated_system.py --symbols AAPL,MSFT --capital 50000 --no-simulation --no-metrics

# Full featured worker
python integrated_system.py --symbols AAPL,MSFT,GOOGL,AMZN,NVDA,TSLA,META --capital 250000 --interval 2.0 --metrics-port 9090
```

### 5. Service Communication

The worker service exposes Prometheus metrics on port 9090 (configurable). To access these:

1. **Option A**: Make worker metrics port public in Railway and configure Prometheus to scrape it
2. **Option B**: Use Railway's internal networking to connect services
3. **Option C**: Export metrics to InfluxDB and visualize in Grafana

The web service `/metrics` endpoint can expose shared metrics if both services run in the same process, but typically:
- **Web service** handles HTTP traffic
- **Worker service** handles market data processing and exposes its own metrics

### 6. Local vs Railway Differences

| Aspect | Local Development | Railway Production |
|--------|------------------|-------------------|
| Infrastructure | `docker-compose up` | Managed services (Redis, MySQL) |
| Configuration | `.env` file | Railway environment variables |
| Networking | localhost | Internal Railway networking |
| Python | Any version | 3.11.x (pinned) |
| Deployment | Manual `python` commands | Automatic via git push |

**Important**: `docker-compose.yml` is for local development only. Do not use it on Railway.

### 7. Monitoring on Railway

#### Logs
View logs in Railway dashboard:
- Web service: HTTP access logs, FastAPI output
- Worker service: Market data processing, trading activity

#### Metrics
- Web service exposes basic health at `/health` and `/status`
- Worker service can expose Prometheus metrics on dedicated port
- Use Railway's built-in metrics for CPU, memory, network

#### Alerts
Configure Railway to:
- Restart services on health check failures
- Alert on high error rates
- Scale based on resource usage

### 8. Database Initialization

Before running the worker, initialize the MySQL database:

```sql
-- Connect to MySQL (via Railway CLI or database client)
CREATE DATABASE IF NOT EXISTS market_memory;

-- Import schema
USE market_memory;
SOURCE init-db.sql;
```

Or use Railway's MySQL import feature to upload `init-db.sql`.

### 9. Troubleshooting Railway Deployment

#### Build Fails with numpy Error
- **Cause**: Python 3.13.x incompatibility
- **Solution**: Verify `.python-version` and `runtime.txt` both specify `3.11.8`

#### Service Crashes on Startup
- **Check**: Environment variables are set correctly
- **Check**: Database services are running and accessible
- **Check**: Start command is correct

#### Cannot Connect to Database
- **Solution**: Use Railway's internal URLs (e.g., `mysql.railway.internal`)
- **Check**: Database service is in same project
- **Check**: Environment variables match Railway's provided values

#### Web Service Shows "502 Bad Gateway"
- **Check**: Start command binds to `0.0.0.0:$PORT`
- **Check**: Health check endpoint `/health` returns 200 OK
- **Wait**: Service may still be starting (check logs)

#### Worker Service Stops Unexpectedly
- **Check**: Memory limits (increase if needed)
- **Check**: Error logs for exceptions
- **Ensure**: Signal handlers work (SIGTERM for graceful shutdown)

### 10. Scaling Considerations

- **Web Service**: Can scale horizontally (multiple instances)
  - Stateless design allows load balancing
  - Railway handles load balancing automatically

- **Worker Service**: Typically runs as single instance
  - Processes market data continuously
  - For multiple workers, ensure coordination (separate symbols or time ranges)

### 11. Cost Optimization

- Use Railway's free tier for testing
- For production:
  - Right-size worker resources (monitor CPU/memory)
  - Use managed Redis/MySQL from Railway
  - Consider external InfluxDB if Railway InfluxDB is expensive
  - Adjust `--interval` to reduce API calls and processing

## ☸️ Production Deployment (Kubernetes)

### 1. Prepare Cluster
# Create namespace
kubectl create namespace market-system

# Apply secrets (edit first!)
kubectl apply -f kubernetes_deployment.yaml

# Verify
kubectl get pods -n market-system
### 2. Configure Auto-scaling
The HPA is pre-configured to scale based on:
CPU utilization (70% target)
Memory utilization (80% target)
Min replicas: 2
Max replicas: 10
# Check HPA status
kubectl get hpa -n market-system

# Manual scaling (if needed)
kubectl scale deployment market-publisher -n market-system --replicas=5
### 3. Persistent Storage
# Check PVCs
kubectl get pvc -n market-system

# Resize if needed (if storage class supports it)
kubectl patch pvc redis-pvc -n market-system -p '{"spec":{"resources":{"requests":{"storage":"20Gi"}}}}'
### 4. Configure Ingress (Optional)
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: market-system-ingress
  namespace: market-system
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - market.example.com
    secretName: market-tls
  rules:
  - host: market.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: grafana-service
            port:
              number: 3000
### 5. Monitoring Setup
# Install Prometheus Operator
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
    -n monitoring --create-namespace

# Import Grafana dashboard
kubectl create configmap grafana-dashboard \
    --from-file=grafana_dashboard.json \
    -n monitoring
📊 Monitoring & Observability
Key Metrics to Monitor
System Health
market_system_service_up - Service availability (0/1)
market_system_circuit_breaker_state - Circuit breaker status
market_system_errors_total - Error counts by component
Data Pipeline
market_system_data_fetch_duration_seconds - Fetch latency
market_system_data_fetch_total - Fetch success/failure rate
market_system_data_points_published_total - Throughput
Portfolio Performance
market_system_portfolio_value_dollars - Current value
market_system_portfolio_pnl_dollars - P&L (realized/unrealized)
market_system_win_rate - Trading win rate
market_system_trade_pnl_dollars - P&L distribution
Simulation
market_system_simulation_global_state - Global Z³ value
market_system_simulation_signals_total - Signal distribution
Alerting Rules
# prometheus-alerts.yaml
groups:
- name: market_system
  interval: 30s
  rules:
  - alert: ServiceDown
    expr: market_system_service_up == 0
    for: 2m
    annotations:
      summary: "Service {{ $labels.service }} is down"
    
  - alert: HighErrorRate
    expr: rate(market_system_errors_total[5m]) > 10
    for: 5m
    annotations:
      summary: "High error rate in {{ $labels.component }}"
    
  - alert: PortfolioLargeDrawdown
    expr: market_system_portfolio_pnl_dollars < -5000
    for: 1m
    annotations:
      summary: "Portfolio P&L below -$5000"
Log Aggregation
# Using Loki for log aggregation
helm install loki grafana/loki-stack \
    -n monitoring \
    --set promtail.enabled=true

# View logs in Grafana
# Add Loki datasource, then query:
# {namespace="market-system", app="market-publisher"}
⚙️ Configuration
Environment Variables
# Data Sources
POLYGON_API_KEY=            # Polygon.io API key
ALPACA_KEY=                 # Alpaca API key
ALPACA_SECRET=              # Alpaca secret

# Databases
REDIS_HOST=localhost
REDIS_PORT=6379
MYSQL_HOST=localhost
MYSQL_USER=market
MYSQL_PASSWORD=            # Secure password
MYSQL_DB=market_memory

# Time-Series
INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=            # InfluxDB auth token
INFLUXDB_ORG=market-system
INFLUXDB_BUCKET=market-data

# Metrics
METRICS_PORT=9090

# ZMQ
ZMQ_PORT=5555
Portfolio Risk Parameters
Edit in portfolio_manager.py or pass to constructor:
PortfolioManager(
    initial_capital=100000,      # Starting capital
    max_position_size=0.10,      # 10% max per position
    max_total_exposure=0.80,     # 80% max deployed
    stop_loss_pct=0.05,          # 5% stop loss
    take_profit_pct=0.15,        # 15% take profit
    max_daily_loss=0.03          # 3% daily drawdown limit
)
Simulation Parameters
Edit in simulation.py:
NUM_BASE_TICKERS = 20       # Base securities
DERIVS_PER_TICKER = 5       # Derivatives per ticker
CROSS_SAMPLE_K = 10         # Cross-sampling factor
ETA = 0.4                   # Noise scaling
PHI_LADDER = [0.3, 0.8, 1.618]  # Golden ratio harmonics
UPDATE_INTERVAL = 0.1       # Update frequency (seconds)
🔧 Troubleshooting
Common Issues
1. Redis Connection Failed
# Check Redis status
docker-compose ps redis
redis-cli ping

# Restart
docker-compose restart redis
2. MySQL Connection Error
# Check logs
docker-compose logs mysql

# Recreate database
docker-compose exec mysql mysql -u root -p
CREATE DATABASE IF NOT EXISTS market_memory;
3. InfluxDB Token Issues
# Get token from InfluxDB UI or create new one
docker-compose exec influxdb influx auth list

# Set in environment
export INFLUXDB_TOKEN="your-token"
4. GPU Not Detected (Simulation)
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# Force CPU mode
export CUDA_VISIBLE_DEVICES=""
5. Circuit Breaker Open
# Check component health
curl http://localhost:9090/metrics | grep circuit_breaker_state

# Restart affected component or wait for retry timeout (60s default)
Debug Mode
# Enable verbose logging
export LOG_LEVEL=DEBUG

# Run with debug flag
python integrated_system.py --debug

# Check specific component
python -c "
from market_system import SentimentEngine
import logging
logging.basicConfig(level=logging.DEBUG)
s = SentimentEngine()
print(s.snapshot())
"
Performance Tuning
High CPU Usage
Reduce NUM_BASE_TICKERS in simulation
Increase UPDATE_INTERVAL
Disable GPU if overhead is high for small models
High Memory Usage
Reduce InfluxDB batch size
Limit portfolio history depth
Enable Redis memory limits: maxmemory 256mb
Slow Data Fetching
Check API rate limits
Enable caching in Redis
Use batch fetching where possible
📚 Additional Resources
API Documentation
Architecture Deep Dive
Contributing Guide
Changelog
🆘 Support
GitHub Issues: [Issues page]
Documentation: [Wiki]
Email: support@example.com
📝 License
[Your License Here]
