import { int, mysqlEnum, mysqlTable, text, timestamp, varchar, decimal, boolean, float, json } from "drizzle-orm/mysql-core";

/**
 * Core user table backing auth flow.
 * Extend this file with additional tables as your product grows.
 * Columns use camelCase to match both database fields and generated types.
 */
export const users = mysqlTable("users", {
  /**
   * Surrogate primary key. Auto-incremented numeric value managed by the database.
   * Use this for relations between tables.
   */
  id: int("id").autoincrement().primaryKey(),
  /** Manus OAuth identifier (openId) returned from the OAuth callback. Unique per user. */
  openId: varchar("openId", { length: 64 }).notNull().unique(),
  name: text("name"),
  email: varchar("email", { length: 320 }),
  loginMethod: varchar("loginMethod", { length: 64 }),
  role: mysqlEnum("role", ["user", "admin"]).default("user").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  lastSignedIn: timestamp("lastSignedIn").defaultNow().notNull(),
});

export type User = typeof users.$inferSelect;
export type InsertUser = typeof users.$inferInsert;

// Market Intelligence Tables

// Live market data snapshots
export const marketData = mysqlTable("market_data", {
  id: int("id").autoincrement().primaryKey(),
  symbol: varchar("symbol", { length: 50 }).notNull(),
  price: decimal("price", { precision: 20, scale: 8 }).notNull(),
  volume: decimal("volume", { precision: 20, scale: 2 }).notNull(),
  sentiment: decimal("sentiment", { precision: 5, scale: 4 }),
  source: varchar("source", { length: 50 }).notNull(),
  recordedAt: timestamp("recordedAt").defaultNow().notNull(),
});

export type MarketData = typeof marketData.$inferSelect;
export type InsertMarketData = typeof marketData.$inferInsert;

// Portfolio positions
export const portfolioPositions = mysqlTable("portfolio_positions", {
  id: int("id").autoincrement().primaryKey(),
  symbol: varchar("symbol", { length: 50 }).notNull(),
  quantity: decimal("quantity", { precision: 20, scale: 8 }).notNull(),
  entryPrice: decimal("entryPrice", { precision: 20, scale: 8 }).notNull(),
  currentPrice: decimal("currentPrice", { precision: 20, scale: 8 }).notNull(),
  stopLoss: decimal("stopLoss", { precision: 20, scale: 8 }),
  takeProfit: decimal("takeProfit", { precision: 20, scale: 8 }),
  unrealizedPnl: decimal("unrealizedPnl", { precision: 20, scale: 2 }).notNull(),
  pnlPercent: decimal("pnlPercent", { precision: 10, scale: 4 }).notNull(),
  openedAt: timestamp("openedAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export type PortfolioPosition = typeof portfolioPositions.$inferSelect;
export type InsertPortfolioPosition = typeof portfolioPositions.$inferInsert;

// Simulation states (Z³ values)
export const simulationStates = mysqlTable("simulation_states", {
  id: int("id").autoincrement().primaryKey(),
  step: int("step").notNull(),
  globalState: decimal("globalState", { precision: 20, scale: 8 }).notNull(),
  activeSignals: int("activeSignals").notNull(),
  agentPrices: json("agentPrices"),
  recordedAt: timestamp("recordedAt").defaultNow().notNull(),
});

export type SimulationState = typeof simulationStates.$inferSelect;
export type InsertSimulationState = typeof simulationStates.$inferInsert;

// Microservices health monitoring
export const microservicesHealth = mysqlTable("microservices_health", {
  id: int("id").autoincrement().primaryKey(),
  service: varchar("service", { length: 100 }).notNull(),
  isHealthy: boolean("isHealthy").notNull(),
  latencyMs: decimal("latencyMs", { precision: 10, scale: 2 }),
  errorCount: int("errorCount").default(0),
  lastError: text("lastError"),
  checkedAt: timestamp("checkedAt").defaultNow().notNull(),
});

export type MicroservicesHealth = typeof microservicesHealth.$inferSelect;
export type InsertMicroservicesHealth = typeof microservicesHealth.$inferInsert;

// Alert rules and circuit breakers
export const alertRules = mysqlTable("alert_rules", {
  id: int("id").autoincrement().primaryKey(),
  name: varchar("name", { length: 255 }).notNull(),
  type: mysqlEnum("type", ["circuit_breaker", "drawdown", "error_rate", "latency"]).notNull(),
  threshold: decimal("threshold", { precision: 10, scale: 4 }).notNull(),
  isActive: boolean("isActive").default(true),
  metadata: json("metadata"),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export type AlertRule = typeof alertRules.$inferSelect;
export type InsertAlertRule = typeof alertRules.$inferInsert;

// Replay/backtest sessions
export const replaySessions = mysqlTable("replay_sessions", {
  id: int("id").autoincrement().primaryKey(),
  name: varchar("name", { length: 255 }).notNull(),
  startDate: timestamp("startDate").notNull(),
  endDate: timestamp("endDate").notNull(),
  symbols: json("symbols"),
  initialCapital: decimal("initialCapital", { precision: 20, scale: 2 }).notNull(),
  status: mysqlEnum("status", ["pending", "running", "completed", "failed"]).default("pending"),
  results: json("results"),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  completedAt: timestamp("completedAt"),
});

export type ReplaySession = typeof replaySessions.$inferSelect;
export type InsertReplaySession = typeof replaySessions.$inferInsert;

// Trading signals for position engine
export const tradingSignals = mysqlTable("trading_signals", {
  id: int("id").autoincrement().primaryKey(),
  symbol: varchar("symbol", { length: 50 }).notNull(),
  signal: mysqlEnum("signal", ["BUY", "SELL", "HOLD"]).notNull(),
  confidence: decimal("confidence", { precision: 5, scale: 4 }).notNull(),
  price: decimal("price", { precision: 20, scale: 8 }).notNull(),
  reason: text("reason"),
  executedAt: timestamp("executedAt"),
  generatedAt: timestamp("generatedAt").defaultNow().notNull(),
});

export type TradingSignal = typeof tradingSignals.$inferSelect;
export type InsertTradingSignal = typeof tradingSignals.$inferInsert;

// Portfolio performance snapshots
export const portfolioSnapshots = mysqlTable("portfolio_snapshots", {
  id: int("id").autoincrement().primaryKey(),
  totalValue: decimal("totalValue", { precision: 20, scale: 2 }).notNull(),
  capital: decimal("capital", { precision: 20, scale: 2 }).notNull(),
  closedPnl: decimal("closedPnl", { precision: 20, scale: 2 }).notNull(),
  unrealizedPnl: decimal("unrealizedPnl", { precision: 20, scale: 2 }).notNull(),
  positionsCount: int("positionsCount").notNull(),
  sharpeRatio: decimal("sharpeRatio", { precision: 10, scale: 4 }),
  maxDrawdown: decimal("maxDrawdown", { precision: 10, scale: 4 }),
  winRate: decimal("winRate", { precision: 5, scale: 4 }),
  snapshotAt: timestamp("snapshotAt").defaultNow().notNull(),
});

export type PortfolioSnapshot = typeof portfolioSnapshots.$inferSelect;
export type InsertPortfolioSnapshot = typeof portfolioSnapshots.$inferInsert;