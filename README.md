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
☸️ Production Deployment (Kubernetes)
1. Prepare Cluster
# Create namespace
kubectl create namespace market-system

# Apply secrets (edit first!)
kubectl apply -f kubernetes_deployment.yaml

# Verify
kubectl get pods -n market-system
2. Configure Auto-scaling
The HPA is pre-configured to scale based on:
CPU utilization (70% target)
Memory utilization (80% target)
Min replicas: 2
Max replicas: 10
# Check HPA status
kubectl get hpa -n market-system

# Manual scaling (if needed)
kubectl scale deployment market-publisher -n market-system --replicas=5
3. Persistent Storage
# Check PVCs
kubectl get pvc -n market-system

# Resize if needed (if storage class supports it)
kubectl patch pvc redis-pvc -n market-system -p '{"spec":{"resources":{"requests":{"storage":"20Gi"}}}}'
4. Configure Ingress (Optional)
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
5. Monitoring Setup
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
