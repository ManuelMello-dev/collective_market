import { eq, desc, and, gte, lte } from "drizzle-orm";
import {
  marketData,
  portfolioPositions,
  simulationStates,
  microservicesHealth,
  alertRules,
  replaySessions,
  tradingSignals,
  portfolioSnapshots,
} from "../drizzle/schema";
import { getDb } from "./db";

// Market Data Queries
export async function getLatestMarketData(symbol: string) {
  const db = await getDb();
  if (!db) return null;

  const result = await db
    .select()
    .from(marketData)
    .where(eq(marketData.symbol, symbol))
    .orderBy(desc(marketData.recordedAt))
    .limit(1);

  return result[0] || null;
}

export async function getMarketDataRange(
  symbol: string,
  startTime: Date,
  endTime: Date
) {
  const db = await getDb();
  if (!db) return [];

  return await db
    .select()
    .from(marketData)
    .where(
      and(
        eq(marketData.symbol, symbol),
        gte(marketData.recordedAt, startTime),
        lte(marketData.recordedAt, endTime)
      )
    )
    .orderBy(desc(marketData.recordedAt));
}

export async function recordMarketData(
  symbol: string,
  price: number,
  volume: number,
  sentiment: number | null,
  source: string
) {
  const db = await getDb();
  if (!db) return null;

  const result = await db.insert(marketData).values({
    symbol,
    price: price.toString(),
    volume: volume.toString(),
    sentiment: sentiment ? sentiment.toString() : null,
    source,
  });

  return result;
}

// Portfolio Position Queries
export async function getOpenPositions() {
  const db = await getDb();
  if (!db) return [];

  return await db.select().from(portfolioPositions);
}

export async function getPositionBySymbol(symbol: string) {
  const db = await getDb();
  if (!db) return null;

  const result = await db
    .select()
    .from(portfolioPositions)
    .where(eq(portfolioPositions.symbol, symbol));

  return result[0] || null;
}

export async function updatePosition(
  symbol: string,
  currentPrice: number,
  unrealizedPnl: number,
  pnlPercent: number
) {
  const db = await getDb();
  if (!db) return null;

  return await db
    .update(portfolioPositions)
    .set({
      currentPrice: currentPrice.toString(),
      unrealizedPnl: unrealizedPnl.toString(),
      pnlPercent: pnlPercent.toString(),
      updatedAt: new Date(),
    })
    .where(eq(portfolioPositions.symbol, symbol));
}

export async function createPosition(
  symbol: string,
  quantity: number,
  entryPrice: number,
  currentPrice: number,
  stopLoss: number | null,
  takeProfit: number | null,
  unrealizedPnl: number,
  pnlPercent: number
) {
  const db = await getDb();
  if (!db) return null;

  return await db.insert(portfolioPositions).values({
    symbol,
    quantity: quantity.toString(),
    entryPrice: entryPrice.toString(),
    currentPrice: currentPrice.toString(),
    stopLoss: stopLoss ? stopLoss.toString() : null,
    takeProfit: takeProfit ? takeProfit.toString() : null,
    unrealizedPnl: unrealizedPnl.toString(),
    pnlPercent: pnlPercent.toString(),
  });
}

export async function closePosition(symbol: string) {
  const db = await getDb();
  if (!db) return null;

  return await db
    .delete(portfolioPositions)
    .where(eq(portfolioPositions.symbol, symbol));
}

// Simulation State Queries
export async function getLatestSimulationState() {
  const db = await getDb();
  if (!db) return null;

  const result = await db
    .select()
    .from(simulationStates)
    .orderBy(desc(simulationStates.recordedAt))
    .limit(1);

  return result[0] || null;
}

export async function recordSimulationState(
  step: number,
  globalState: number,
  activeSignals: number,
  agentPrices: Record<string, number> | null
) {
  const db = await getDb();
  if (!db) return null;

  return await db.insert(simulationStates).values({
    step,
    globalState: globalState.toString(),
    activeSignals,
    agentPrices: agentPrices ? JSON.stringify(agentPrices) : null,
  });
}

// Microservices Health Queries
export async function getServiceHealth(service: string) {
  const db = await getDb();
  if (!db) return null;

  const result = await db
    .select()
    .from(microservicesHealth)
    .where(eq(microservicesHealth.service, service))
    .orderBy(desc(microservicesHealth.checkedAt))
    .limit(1);

  return result[0] || null;
}

export async function getAllServicesHealth() {
  const db = await getDb();
  if (!db) return [];

  return await db
    .select()
    .from(microservicesHealth)
    .orderBy(desc(microservicesHealth.checkedAt));
}

export async function recordServiceHealth(
  service: string,
  isHealthy: boolean,
  latencyMs: number | null,
  errorCount: number,
  lastError: string | null
) {
  const db = await getDb();
  if (!db) return null;

  return await db.insert(microservicesHealth).values({
    service,
    isHealthy,
    latencyMs: latencyMs ? latencyMs.toString() : null,
    errorCount,
    lastError,
  });
}

// Alert Rules Queries
export async function getAlertRules() {
  const db = await getDb();
  if (!db) return [];

  return await db.select().from(alertRules);
}

export async function getActiveAlertRules() {
  const db = await getDb();
  if (!db) return [];

  return await db
    .select()
    .from(alertRules)
    .where(eq(alertRules.isActive, true));
}

export async function createAlertRule(
  name: string,
  type: "circuit_breaker" | "drawdown" | "error_rate" | "latency",
  threshold: number,
  metadata: Record<string, unknown> | null
) {
  const db = await getDb();
  if (!db) return null;

  return await db.insert(alertRules).values({
    name,
    type,
    threshold: threshold.toString(),
    metadata: metadata ? JSON.stringify(metadata) : null,
  });
}

export async function updateAlertRule(
  id: number,
  isActive: boolean,
  threshold: number | null
) {
  const db = await getDb();
  if (!db) return null;

  const updates: Record<string, unknown> = {
    isActive,
    updatedAt: new Date(),
  };

  if (threshold !== null) {
    updates.threshold = threshold.toString();
  }

  return await db
    .update(alertRules)
    .set(updates)
    .where(eq(alertRules.id, id));
}

// Trading Signals Queries
export async function getLatestSignals(limit: number = 10) {
  const db = await getDb();
  if (!db) return [];

  return await db
    .select()
    .from(tradingSignals)
    .orderBy(desc(tradingSignals.generatedAt))
    .limit(limit);
}

export async function recordTradingSignal(
  symbol: string,
  signal: "BUY" | "SELL" | "HOLD",
  confidence: number,
  price: number,
  reason: string | null
) {
  const db = await getDb();
  if (!db) return null;

  return await db.insert(tradingSignals).values({
    symbol,
    signal,
    confidence: confidence.toString(),
    price: price.toString(),
    reason,
  });
}

// Portfolio Snapshots Queries
export async function getLatestPortfolioSnapshot() {
  const db = await getDb();
  if (!db) return null;

  const result = await db
    .select()
    .from(portfolioSnapshots)
    .orderBy(desc(portfolioSnapshots.snapshotAt))
    .limit(1);

  return result[0] || null;
}

export async function getPortfolioSnapshotRange(
  startTime: Date,
  endTime: Date
) {
  const db = await getDb();
  if (!db) return [];

  return await db
    .select()
    .from(portfolioSnapshots)
    .where(
      and(
        gte(portfolioSnapshots.snapshotAt, startTime),
        lte(portfolioSnapshots.snapshotAt, endTime)
      )
    )
    .orderBy(desc(portfolioSnapshots.snapshotAt));
}

export async function recordPortfolioSnapshot(
  totalValue: number,
  capital: number,
  closedPnl: number,
  unrealizedPnl: number,
  positionsCount: number,
  sharpeRatio: number | null,
  maxDrawdown: number | null,
  winRate: number | null
) {
  const db = await getDb();
  if (!db) return null;

  return await db.insert(portfolioSnapshots).values({
    totalValue: totalValue.toString(),
    capital: capital.toString(),
    closedPnl: closedPnl.toString(),
    unrealizedPnl: unrealizedPnl.toString(),
    positionsCount,
    sharpeRatio: sharpeRatio ? sharpeRatio.toString() : null,
    maxDrawdown: maxDrawdown ? maxDrawdown.toString() : null,
    winRate: winRate ? winRate.toString() : null,
  });
}

// Replay Sessions Queries
export async function getReplaySessions() {
  const db = await getDb();
  if (!db) return [];

  return await db
    .select()
    .from(replaySessions)
    .orderBy(desc(replaySessions.createdAt));
}

export async function createReplaySession(
  name: string,
  startDate: Date,
  endDate: Date,
  symbols: string[],
  initialCapital: number
) {
  const db = await getDb();
  if (!db) return null;

  return await db.insert(replaySessions).values({
    name,
    startDate,
    endDate,
    symbols: JSON.stringify(symbols),
    initialCapital: initialCapital.toString(),
  });
}

export async function updateReplaySessionStatus(
  id: number,
  status: "pending" | "running" | "completed" | "failed",
  results: Record<string, unknown> | null
) {
  const db = await getDb();
  if (!db) return null;

  const updates: Record<string, unknown> = {
    status,
  };

  if (results) {
    updates.results = JSON.stringify(results);
  }

  if (status === "completed") {
    updates.completedAt = new Date();
  }

  return await db
    .update(replaySessions)
    .set(updates)
    .where(eq(replaySessions.id, id));
}
