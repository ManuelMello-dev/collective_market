# Market Intelligence Dashboard

A **brutalist-styled real-time trading dashboard** built with React 19, Tailwind 4, and tRPC. Provides operational intelligence for the collective_market system with heavy typography, stark contrast, and industrial design.

## Features

### 🎯 Core Dashboards

1. **Market Monitoring** - Live prices, sentiment analysis, volume tracking
2. **Portfolio Performance** - Position management, P&L tracking, Sharpe ratio metrics
3. **Simulation Engine** - Z³ global state, agent dynamics, convergence metrics
4. **Microservices Health** - Service status, latency monitoring, error tracking
5. **Alert Management** - Circuit breakers, drawdown limits, error thresholds

### 🔗 Integration

- **Redis**: Episodic memory for live market state
- **MySQL**: Long-term storage for historical data
- **InfluxDB**: Time-series metrics and analytics
- **ZMQ**: Real-time message bus for live updates

### 🎨 Design

- **Brutalist Aesthetic**: Heavy IBM Plex Sans typography, stark black/white palette
- **High Contrast**: Geometric elements, 4px borders, minimal decoration
- **Industrial Feel**: Abundant negative space, raw unpolished appearance
- **Responsive**: Grid-based layouts, mobile-friendly design

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 22+ (for local development)
- pnpm (for package management)

### Installation

```bash
# Clone repository
git clone https://github.com/ManuelMello-dev/collective_market.git
cd collective_market

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start all services
docker-compose up -d

# Access dashboard
# http://localhost:3000
```

### Local Development

```bash
# Install dependencies
cd dashboard
pnpm install

# Start dev server
pnpm dev

# Run tests
pnpm test

# Build for production
pnpm build
```

## Architecture

```
Dashboard (React + tRPC)
    ↓
Express Backend
    ↓
┌───────────────────────────────────┐
│ Redis │ MySQL │ InfluxDB │ ZMQ   │
└───────────────────────────────────┘
    ↓
Collective Market Services
(Ingestion, Memory Hub, Sim Engine)
```

## File Structure

```
dashboard/
├── client/                 # React frontend
│   ├── src/
│   │   ├── pages/         # Dashboard pages
│   │   ├── components/    # UI components
│   │   ├── lib/           # tRPC client
│   │   └── index.css      # Brutalist design system
│   └── public/            # Static assets
├── server/                # Express backend
│   ├── routers/           # tRPC procedures
│   ├── db.ts              # Database queries
│   ├── integrations.ts    # Redis/InfluxDB/ZMQ
│   └── _core/             # Framework code
├── drizzle/               # Database schema
└── package.json
```

## tRPC Procedures

### Market Data
```typescript
trpc.market.getLatestPrices.useQuery()
trpc.market.getMarketSentiment.useQuery()
```

### Portfolio
```typescript
trpc.portfolio.getPortfolioState.useQuery()
trpc.portfolio.getPerformanceMetrics.useQuery()
```

### Simulation
```typescript
trpc.simulation.getGlobalState.useQuery()
trpc.simulation.getActiveSignals.useQuery()
```

### Health
```typescript
trpc.health.getSystemHealth.useQuery()
trpc.health.getServiceStatus.useQuery()
```

### Alerts
```typescript
trpc.alerts.getAlertRules.useQuery()
trpc.alerts.createAlertRule.useMutation()
```

## Database Schema

The dashboard extends the collective_market database with:

- `market_data` - Live price/volume tracking
- `portfolio_positions` - Position management
- `simulation_states` - Z³ and agent dynamics
- `microservices_health` - Service monitoring
- `alerts_config` - Alert rules
- `replay_sessions` - Backtest configuration
- `trading_signals` - Live signals

See `DASHBOARD_INTEGRATION.md` for full schema details.

## Deployment

### Docker Compose
```bash
docker-compose up -d
```

### Kubernetes
See `kubernetes_deployment.yaml` for production deployment.

### Environment Variables

```env
NODE_ENV=production
DATABASE_URL=mysql://market:password@mysql:3306/market_memory
JWT_SECRET=your-secret-key
REDIS_HOST=redis
REDIS_PORT=6379
INFLUXDB_URL=http://influxdb:8086
INFLUXDB_TOKEN=your-token
```

## Monitoring

- **Dashboard**: http://localhost:3000
- **Grafana**: http://localhost:3000
- **Prometheus**: http://localhost:9090
- **InfluxDB**: http://localhost:8086

## Development

### Add a New Page

1. Create component in `client/src/pages/NewPage.tsx`
2. Add route in `client/src/App.tsx`
3. Add navigation link in `client/src/components/DashboardNav.tsx`
4. Create tRPC procedures in `server/routers/`
5. Write tests in `server/*.test.ts`

### Add a New Feature

1. Update database schema in `drizzle/schema.ts`
2. Run `pnpm db:push` to migrate
3. Create query helpers in `server/market.db.ts`
4. Create tRPC procedures in `server/routers/`
5. Build UI components in `client/src/pages/` or `client/src/components/`
6. Write vitest tests

### Testing

```bash
# Run all tests
pnpm test

# Run specific test
pnpm test server/market.router.test.ts

# Watch mode
pnpm test --watch
```

## Troubleshooting

### Dashboard won't start
```bash
docker-compose logs market-dashboard
```

### No data appearing
1. Verify Redis/MySQL/InfluxDB are healthy
2. Check ingestion service is running
3. Verify environment variables
4. Check database tables: `SELECT COUNT(*) FROM market_data;`

### Performance issues
1. Check service latencies in Health dashboard
2. Review InfluxDB query performance
3. Check MySQL slow query log
4. Monitor Redis memory usage

## Next Steps

- [ ] Real-time WebSocket updates
- [ ] Historical data explorer with time-series charts
- [ ] Replay mode for backtesting
- [ ] Live position engine with paper trading
- [ ] Advanced analytics and ML signals
- [ ] Mobile app

## License

MIT - See LICENSE file

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review service logs
3. Open an issue on GitHub with details
