-- MySQL Initialization Script for Market Intelligence System
-- Creates necessary tables and indexes

USE market_memory;

-- Market events table (long-term storage)
CREATE TABLE IF NOT EXISTS market_events (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(50) NOT NULL,
    payload TEXT,
    ts DOUBLE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_ts (ts),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Trades table
CREATE TABLE IF NOT EXISTS trades (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(50) NOT NULL,
    action ENUM('BUY', 'SELL', 'STOP_LOSS', 'TAKE_PROFIT') NOT NULL,
    quantity DECIMAL(20, 8) NOT NULL,
    price DECIMAL(20, 8) NOT NULL,
    pnl DECIMAL(20, 8),
    reason VARCHAR(100),
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_action (action),
    INDEX idx_executed_at (executed_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Portfolio snapshots table
CREATE TABLE IF NOT EXISTS portfolio_snapshots (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    total_value DECIMAL(20, 2) NOT NULL,
    capital DECIMAL(20, 2) NOT NULL,
    closed_pnl DECIMAL(20, 2) NOT NULL,
    unrealized_pnl DECIMAL(20, 2) NOT NULL,
    positions_count INT NOT NULL,
    snapshot_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_snapshot_at (snapshot_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Performance metrics table
CREATE TABLE IF NOT EXISTS performance_metrics (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sharpe_ratio DECIMAL(10, 4),
    max_drawdown DECIMAL(10, 4),
    win_rate DECIMAL(10, 4),
    total_trades INT,
    winning_trades INT,
    losing_trades INT,
    total_pnl DECIMAL(20, 2),
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_calculated_at (calculated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Simulation states table
CREATE TABLE IF NOT EXISTS simulation_states (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    step INT NOT NULL,
    global_state DECIMAL(20, 8) NOT NULL,
    active_signals INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_step (step),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- System health table
CREATE TABLE IF NOT EXISTS system_health (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    component VARCHAR(100) NOT NULL,
    is_healthy BOOLEAN NOT NULL,
    latency_ms DECIMAL(10, 2),
    error_count INT DEFAULT 0,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_component (component),
    INDEX idx_checked_at (checked_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create views for common queries

-- Recent trades view
CREATE OR REPLACE VIEW recent_trades AS
SELECT 
    symbol,
    action,
    quantity,
    price,
    pnl,
    executed_at
FROM trades
ORDER BY executed_at DESC
LIMIT 100;

-- Daily performance view
CREATE OR REPLACE VIEW daily_performance AS
SELECT 
    DATE(executed_at) as trade_date,
    COUNT(*) as total_trades,
    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
    SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losing_trades,
    SUM(pnl) as daily_pnl,
    AVG(pnl) as avg_pnl,
    MIN(pnl) as worst_trade,
    MAX(pnl) as best_trade
FROM trades
WHERE pnl IS NOT NULL
GROUP BY DATE(executed_at)
ORDER BY trade_date DESC;

-- Portfolio health view
CREATE OR REPLACE VIEW portfolio_health AS
SELECT 
    p.*,
    (p.total_value - LAG(p.total_value) OVER (ORDER BY p.snapshot_at)) / 
    LAG(p.total_value) OVER (ORDER BY p.snapshot_at) * 100 as change_pct
FROM portfolio_snapshots p
ORDER BY p.snapshot_at DESC
LIMIT 100;

-- Initialize with a test record (optional)
-- INSERT INTO system_health (component, is_healthy, latency_ms) 
-- VALUES ('initialization', TRUE, 0);

-- Grant permissions to application user
GRANT SELECT, INSERT, UPDATE, DELETE ON market_memory.* TO 'market'@'%';
FLUSH PRIVILEGES;
