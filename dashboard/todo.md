# Market Intelligence Dashboard - TODO

## Phase 1: Architecture & Integration
- [x] Analyze collective_market microservices architecture
- [x] Design Redis episodic memory integration layer
- [x] Design MySQL long-term memory query patterns
- [x] Design InfluxDB time-series data fetching
- [x] Design ZMQ message bus integration for live updates
- [x] Create integration documentation

## Phase 2: Database Schema Extension
- [x] Create market_data table for live price/volume tracking
- [x] Create portfolio_positions table for position management
- [x] Create simulation_states table for Z³ and agent dynamics
- [x] Create microservices_health table for service monitoring
- [x] Create alerts_config table for circuit breaker rules
- [x] Create replay_sessions table for backtesting
- [x] Create trading_signals table for live position engine
- [x] Run database migrations

## Phase 3: tRPC Procedures & Backend
- [x] Build Redis connection helper for episodic memory
- [x] Build MySQL query helpers for historical data
- [x] Build InfluxDB query helpers for time-series
- [x] Create market.getLatestPrices procedure
- [x] Create market.getMarketSentiment procedure
- [x] Create portfolio.getPortfolioState procedure
- [x] Create portfolio.getPerformanceMetrics procedure
- [x] Create simulation.getGlobalState procedure
- [x] Create simulation.getActiveSignals procedure
- [x] Create health.getServiceStatus procedure
- [x] Create health.getSystemMetrics procedure
- [ ] Create history.getTrades procedure
- [ ] Create history.getPortfolioSnapshots procedure
- [ ] Create history.getPerformanceTrends procedure
- [ ] Create timeseries.getPriceHistory procedure
- [ ] Create timeseries.getPortfolioHistory procedure
- [ ] Create config.updateRiskParameters procedure
- [ ] Create replay.startBacktest procedure
- [ ] Create replay.getBacktestResults procedure
- [ ] Create position.getOpenPositions procedure
- [ ] Create position.submitTrade procedure
- [x] Create alerts.getAlertRules procedure
- [x] Create alerts.updateAlertRule procedure
- [ ] Write vitest tests for all procedures

## Phase 4: UI Design System (Brutalist)
- [x] Define typographic hierarchy (heavy sans-serif)
- [x] Create global CSS variables for stark black/white palette
- [x] Build layout grid system with negative space
- [x] Create geometric divider components (brackets, underlines)
- [x] Build typography scale (H1-H6, body, mono)
- [x] Create color system (black, white, grays)
- [x] Build button component (stark, geometric)
- [x] Build card component (high contrast borders)
- [x] Build input component (minimal, industrial)
- [x] Build table component (grid-based, heavy lines)
- [x] Build chart wrapper component (stark styling)
- [x] Create loading skeleton (geometric patterns)
- [x] Update index.css with brutalist theme

## Phase 5: Real-time Market Monitoring Dashboard
- [x] Build DashboardLayout with sidebar navigation
- [x] Create MarketMonitor component (live prices grid)
- [x] Create SentimentIndicator component (visual display)
- [x] Create VolumeAnalyzer component (attention visualization)
- [ ] Create MarketTicker component (scrolling updates)
- [ ] Implement WebSocket/polling for live data
- [ ] Build price alert notifications
- [ ] Create symbol watchlist management
- [ ] Write component tests

## Phase 6: Portfolio Performance & Simulation Tracking
- [x] Build PortfolioOverview component (key metrics)
- [x] Create PositionManager component (table + actions)
- [ ] Build P&L Visualization component (area chart)
- [x] Create WinRate component (metrics display)
- [x] Build SharpeRatio component (metric card)
- [x] Create SimulationMonitor component (Z³ display)
- [x] Build AgentDynamics component (visualization)
- [ ] Create SignalDistribution component (chart)
- [ ] Implement real-time metric updates
- [ ] Write component tests

## Phase 7: Historical Explorer & Time-Series Charts
- [ ] Build HistoricalExplorer page
- [ ] Create TradeHistoryTable component (sortable, filterable)
- [ ] Build PortfolioSnapshotChart component
- [ ] Create PerformanceTrendsChart component
- [ ] Build PriceHistoryChart component (multi-symbol)
- [ ] Create DrawdownCurve component
- [ ] Build DateRangePicker component
- [ ] Implement data export (CSV)
- [ ] Write component tests

## Phase 8: Microservices Health Dashboard
- [x] Build HealthDashboard page
- [x] Create ServiceStatusCard component (per service)
- [x] Build SystemMetricsPanel component
- [x] Create LatencyMonitor component
- [x] Build ErrorRateDisplay component
- [x] Create ServiceControlPanel component (restart buttons)
- [ ] Build HealthTimeline component
- [ ] Implement auto-refresh logic
- [ ] Write component tests

## Phase 9: Replay Mode, Position Engine & Alerts
- [ ] Build ReplayMode page
- [ ] Create BacktestConfigPanel component
- [ ] Build DataSourceSelector component
- [ ] Create BacktestResultsViewer component
- [ ] Build PositionEngine page
- [ ] Create OpenPositionsPanel component
- [ ] Build TradeExecutionForm component
- [ ] Create PaperTradingToggle component
- [x] Build AlertManagement page
- [ ] Create AlertRuleEditor component
- [x] Build CircuitBreakerPanel component
- [ ] Create AlertNotificationCenter component
- [ ] Write component tests

## Phase 10: Integration & Testing
- [ ] Test Redis connection and data flow
- [ ] Test MySQL queries and historical data
- [ ] Test InfluxDB time-series retrieval
- [ ] Test ZMQ message bus integration
- [ ] Test real-time data updates
- [ ] Test chart rendering with live data
- [ ] Test error handling and fallbacks
- [ ] Test responsive design (mobile, tablet, desktop)
- [ ] Performance testing (load times, chart rendering)
- [ ] Security testing (auth, data access)

## Phase 11: Documentation & Deployment
- [ ] Create API documentation
- [ ] Write integration guide for collective_market
- [ ] Create user guide for dashboard features
- [ ] Document configuration options
- [ ] Create troubleshooting guide
- [ ] Prepare deployment checklist
- [ ] Create checkpoint for deployment
