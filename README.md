Collective Market
Institutional-Grade Market Intelligence & Simulation Engine
collective_market is a modular, high-performance trading ecosystem designed to solve the three critical bottlenecks in quantitative finance:
 * Data Infrastructure: Automated, multi-source ingestion pipelines (Polygon, Alpaca, CCXT) with zero-gap resilience.
 * Quant Simulation: A PyTorch-based multi-agent environment for stress-testing strategies against "Black Swan" events.
 * Operational Monitoring: Full observability stack (Prometheus, Grafana, ZeroMQ) for mission-critical trading ops.
📋 Table of Contents
 * Architecture Overview
 * Quick Start
 * Local Development
 * Production Deployment
 * Monitoring & Observability
 * Configuration
 * Troubleshooting
🏗️ Architecture Overview
System Components
graph TD
    subgraph Data_Layer
    A[Sentiment Engine] -->|ZeroMQ| B[Market Fetcher]
    B -->|ZeroMQ| C[Simulation Engine]
    end
    
    subgraph Core_Logic
    C --> D[Portfolio Manager]
    end
    
    subgraph Storage
    D --> E[(Redis - Hot)]
    D --> F[(MySQL - Cold)]
    D --> G[(InfluxDB - Metrics)]
    end
    
    subgraph Observability
    G --> H[Prometheus]
    H --> I[Grafana]
    end

Data Flow
 * Market Data Collection: Multi-source fetching (yfinance → Polygon → Alpaca → CCXT)
 * Sentiment Analysis: Fear & Greed indices for equity + crypto markets
 * Memory Systems:
   * Redis (episodic, 1-hour TTL)
   * MySQL (long-term archival)
 * Agent Simulation: PyTorch-based multi-agent market dynamics
 * Portfolio Management: Risk-controlled position tracking with stop-loss/take-profit
 * Observability: Prometheus metrics + InfluxDB time-series + Grafana visualization
🚀 Quick Start
Prerequisites
 * Python 3.9+
 * Docker & Docker Compose
 * kubectl (for Kubernetes deployment)
 * 4GB+ RAM
 * Optional: NVIDIA GPU for simulation acceleration
1. Local Docker Compose Setup
# Clone repository
git clone https://github.com/ManuelMello-dev/collective_market.git
cd collective_market

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
 * Grafana: http://localhost:3000 (admin/admin)
 * Prometheus: http://localhost:9090
 * Metrics: http://localhost:9090/metrics
 * InfluxDB: http://localhost:8086
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

☸️ Production Deployment (Railway / K8s)
Railway Auto-Deploy
This repository is configured for Railway. Pushing to main will trigger a build using the Dockerfile in the root. Ensure your Railway environment variables match the .env structure above.
Kubernetes Deployment
# Create namespace
kubectl create namespace market-system

# Apply secrets (edit first!)
kubectl apply -f kubernetes_deployment.yaml

# Verify
kubectl get pods -n market-system

📊 Monitoring & Observability
Key Metrics to Monitor
 * System Health: market_system_service_up, market_system_circuit_breaker_state
 * Data Pipeline: market_system_data_fetch_duration_seconds
 * Portfolio: market_system_portfolio_pnl_dollars (Realized/Unrealized P&L)
 * Simulation: market_system_simulation_global_state (Z³ Value)
Alerting Rules (Prometheus)
The system includes pre-configured alerts for:
 * Service Downtime (> 2m)
 * High Error Rates (> 10 errors/5m)
 * Portfolio Drawdown (P&L < -$5000)
⚙️ Configuration
Environment Variables
# Data Sources
POLYGON_API_KEY=            # Polygon.io API key
ALPACA_KEY=                 # Alpaca API key
ALPACA_SECRET=              # Alpaca secret

# Databases
REDIS_HOST=localhost
MYSQL_HOST=localhost
MYSQL_USER=market
MYSQL_DB=market_memory

# Time-Series
INFLUXDB_URL=http://localhost:8086
INFLUXDB_ORG=market-system
INFLUXDB_BUCKET=market-data
