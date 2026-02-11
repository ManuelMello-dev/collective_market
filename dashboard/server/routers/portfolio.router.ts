import { z } from "zod";
import { publicProcedure, router } from "../_core/trpc";
import * as db from "../market.db";
import { getRedisData, setRedisData } from "../integrations";

export const portfolioRouter = router({
  // Get current portfolio state
  getPortfolioState: publicProcedure.query(async () => {
    try {
      const snapshot = await db.getLatestPortfolioSnapshot();
      if (!snapshot) {
        return {
          totalValue: 100000,
          capital: 100000,
          closedPnl: 0,
          unrealizedPnl: 0,
          positionsCount: 0,
          sharpeRatio: 0,
          maxDrawdown: 0,
          winRate: 0,
        };
      }

      return {
        totalValue: parseFloat(snapshot.totalValue as unknown as string),
        capital: parseFloat(snapshot.capital as unknown as string),
        closedPnl: parseFloat(snapshot.closedPnl as unknown as string),
        unrealizedPnl: parseFloat(snapshot.unrealizedPnl as unknown as string),
        positionsCount: snapshot.positionsCount,
        sharpeRatio: snapshot.sharpeRatio
          ? parseFloat(snapshot.sharpeRatio as unknown as string)
          : 0,
        maxDrawdown: snapshot.maxDrawdown
          ? parseFloat(snapshot.maxDrawdown as unknown as string)
          : 0,
        winRate: snapshot.winRate
          ? parseFloat(snapshot.winRate as unknown as string)
          : 0,
        snapshotAt: snapshot.snapshotAt,
      };
    } catch (error) {
      console.error("Failed to get portfolio state:", error);
      throw error;
    }
  }),

  // Get open positions
  getOpenPositions: publicProcedure.query(async () => {
    try {
      const positions = await db.getOpenPositions();
      return positions.map((p) => ({
        symbol: p.symbol,
        quantity: parseFloat(p.quantity as unknown as string),
        entryPrice: parseFloat(p.entryPrice as unknown as string),
        currentPrice: parseFloat(p.currentPrice as unknown as string),
        stopLoss: p.stopLoss
          ? parseFloat(p.stopLoss as unknown as string)
          : null,
        takeProfit: p.takeProfit
          ? parseFloat(p.takeProfit as unknown as string)
          : null,
        unrealizedPnl: parseFloat(p.unrealizedPnl as unknown as string),
        pnlPercent: parseFloat(p.pnlPercent as unknown as string),
        openedAt: p.openedAt,
      }));
    } catch (error) {
      console.error("Failed to get open positions:", error);
      throw error;
    }
  }),

  // Get position by symbol
  getPosition: publicProcedure
    .input(z.object({ symbol: z.string() }))
    .query(async ({ input }) => {
      try {
        const position = await db.getPositionBySymbol(input.symbol);
        if (!position) return null;

        return {
          symbol: position.symbol,
          quantity: parseFloat(position.quantity as unknown as string),
          entryPrice: parseFloat(position.entryPrice as unknown as string),
          currentPrice: parseFloat(position.currentPrice as unknown as string),
          stopLoss: position.stopLoss
            ? parseFloat(position.stopLoss as unknown as string)
            : null,
          takeProfit: position.takeProfit
            ? parseFloat(position.takeProfit as unknown as string)
            : null,
          unrealizedPnl: parseFloat(position.unrealizedPnl as unknown as string),
          pnlPercent: parseFloat(position.pnlPercent as unknown as string),
          openedAt: position.openedAt,
        };
      } catch (error) {
        console.error("Failed to get position:", error);
        throw error;
      }
    }),

  // Update position price (for real-time updates)
  updatePositionPrice: publicProcedure
    .input(
      z.object({
        symbol: z.string(),
        currentPrice: z.number(),
      })
    )
    .mutation(async ({ input }) => {
      try {
        const position = await db.getPositionBySymbol(input.symbol);
        if (!position) throw new Error("Position not found");

        const quantity = parseFloat(position.quantity as unknown as string);
        const entryPrice = parseFloat(position.entryPrice as unknown as string);
        const unrealizedPnl = quantity * (input.currentPrice - entryPrice);
        const pnlPercent =
          ((input.currentPrice - entryPrice) / entryPrice) * 100;

        await db.updatePosition(
          input.symbol,
          input.currentPrice,
          unrealizedPnl,
          pnlPercent
        );

        return { success: true };
      } catch (error) {
        console.error("Failed to update position price:", error);
        throw error;
      }
    }),

  // Get performance metrics
  getPerformanceMetrics: publicProcedure.query(async () => {
    try {
      const snapshot = await db.getLatestPortfolioSnapshot();
      if (!snapshot) {
        return {
          totalTrades: 0,
          winningTrades: 0,
          losingTrades: 0,
          winRate: 0,
          sharpeRatio: 0,
          maxDrawdown: 0,
          totalPnl: 0,
        };
      }

      return {
        totalTrades: 0, // Would be calculated from trades table
        winningTrades: 0,
        losingTrades: 0,
        winRate: snapshot.winRate
          ? parseFloat(snapshot.winRate as unknown as string)
          : 0,
        sharpeRatio: snapshot.sharpeRatio
          ? parseFloat(snapshot.sharpeRatio as unknown as string)
          : 0,
        maxDrawdown: snapshot.maxDrawdown
          ? parseFloat(snapshot.maxDrawdown as unknown as string)
          : 0,
        totalPnl: parseFloat(snapshot.closedPnl as unknown as string),
      };
    } catch (error) {
      console.error("Failed to get performance metrics:", error);
      throw error;
    }
  }),

  // Get portfolio value history
  getPortfolioHistory: publicProcedure
    .input(
      z.object({
        startTime: z.date(),
        endTime: z.date(),
      })
    )
    .query(async ({ input }) => {
      try {
        const snapshots = await db.getPortfolioSnapshotRange(
          input.startTime,
          input.endTime
        );

        return snapshots.map((s) => ({
          totalValue: parseFloat(s.totalValue as unknown as string),
          capital: parseFloat(s.capital as unknown as string),
          closedPnl: parseFloat(s.closedPnl as unknown as string),
          unrealizedPnl: parseFloat(s.unrealizedPnl as unknown as string),
          snapshotAt: s.snapshotAt,
        }));
      } catch (error) {
        console.error("Failed to get portfolio history:", error);
        throw error;
      }
    }),

  // Record portfolio snapshot
  recordSnapshot: publicProcedure
    .input(
      z.object({
        totalValue: z.number(),
        capital: z.number(),
        closedPnl: z.number(),
        unrealizedPnl: z.number(),
        positionsCount: z.number(),
        sharpeRatio: z.number().optional(),
        maxDrawdown: z.number().optional(),
        winRate: z.number().optional(),
      })
    )
    .mutation(async ({ input }) => {
      try {
        await db.recordPortfolioSnapshot(
          input.totalValue,
          input.capital,
          input.closedPnl,
          input.unrealizedPnl,
          input.positionsCount,
          input.sharpeRatio || null,
          input.maxDrawdown || null,
          input.winRate || null
        );

        // Cache in Redis
        await setRedisData(
          "portfolio:latest",
          {
            totalValue: input.totalValue,
            capital: input.capital,
            closedPnl: input.closedPnl,
            unrealizedPnl: input.unrealizedPnl,
            positionsCount: input.positionsCount,
            timestamp: new Date(),
          },
          3600 // 1 hour TTL
        );

        return { success: true };
      } catch (error) {
        console.error("Failed to record snapshot:", error);
        throw error;
      }
    }),
});
