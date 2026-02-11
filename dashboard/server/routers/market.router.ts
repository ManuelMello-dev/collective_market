import { z } from "zod";
import { publicProcedure, router } from "../_core/trpc";
import * as db from "../market.db";
import {
  getRedisData,
  setRedisData,
  queryMySQL,
  getSystemHealth,
} from "../integrations";

export const marketRouter = router({
  // Get latest market data for a symbol
  getLatestPrice: publicProcedure
    .input(z.object({ symbol: z.string() }))
    .query(async ({ input }) => {
      const data = await db.getLatestMarketData(input.symbol);
      return data
        ? {
            symbol: data.symbol,
            price: parseFloat(data.price as unknown as string),
            volume: parseFloat(data.volume as unknown as string),
            sentiment: data.sentiment
              ? parseFloat(data.sentiment as unknown as string)
              : null,
            source: data.source,
            recordedAt: data.recordedAt,
          }
        : null;
    }),

  // Get market data range for charting
  getPriceHistory: publicProcedure
    .input(
      z.object({
        symbol: z.string(),
        startTime: z.date(),
        endTime: z.date(),
      })
    )
    .query(async ({ input }) => {
      const data = await db.getMarketDataRange(
        input.symbol,
        input.startTime,
        input.endTime
      );

      return data.map((d) => ({
        symbol: d.symbol,
        price: parseFloat(d.price as unknown as string),
        volume: parseFloat(d.volume as unknown as string),
        sentiment: d.sentiment
          ? parseFloat(d.sentiment as unknown as string)
          : null,
        source: d.source,
        recordedAt: d.recordedAt,
      }));
    }),

  // Get market sentiment from Redis episodic memory
  getMarketSentiment: publicProcedure.query(async () => {
    try {
      const sentiment = await getRedisData("market:sentiment");
      return sentiment || { equity: 0.5, crypto: 0.5, timestamp: new Date() };
    } catch (error) {
      console.error("Failed to get market sentiment:", error);
      return { equity: 0.5, crypto: 0.5, timestamp: new Date() };
    }
  }),

  // Get attention (volume) analysis
  getVolumeAnalysis: publicProcedure
    .input(z.object({ symbol: z.string() }))
    .query(async ({ input }) => {
      try {
        const key = `market:volume:${input.symbol}`;
        const data = await getRedisData(key);
        return data || { symbol: input.symbol, volume: 0, attention: 0 };
      } catch (error) {
        console.error("Failed to get volume analysis:", error);
        return { symbol: input.symbol, volume: 0, attention: 0 };
      }
    }),

  // Record market data point
  recordPrice: publicProcedure
    .input(
      z.object({
        symbol: z.string(),
        price: z.number(),
        volume: z.number(),
        sentiment: z.number().optional(),
        source: z.string(),
      })
    )
    .mutation(async ({ input }) => {
      try {
        await db.recordMarketData(
          input.symbol,
          input.price,
          input.volume,
          input.sentiment || null,
          input.source
        );

        // Also cache in Redis for fast access
        await setRedisData(
          `market:latest:${input.symbol}`,
          {
            symbol: input.symbol,
            price: input.price,
            volume: input.volume,
            sentiment: input.sentiment,
            recordedAt: new Date(),
          },
          3600 // 1 hour TTL
        );

        return { success: true };
      } catch (error) {
        console.error("Failed to record price:", error);
        throw error;
      }
    }),

  // Get system health
  getSystemHealth: publicProcedure.query(async () => {
    try {
      return await getSystemHealth();
    } catch (error) {
      console.error("Failed to get system health:", error);
      return {
        redis: false,
        influxdb: false,
        mysql: false,
        zmq: false,
        timestamp: new Date().toISOString(),
      };
    }
  }),

  // Get watchlist
  getWatchlist: publicProcedure.query(async () => {
    try {
      const watchlist = await getRedisData("market:watchlist");
      return (watchlist as string[]) || [];
    } catch (error) {
      console.error("Failed to get watchlist:", error);
      return [];
    }
  }),

  // Update watchlist
  updateWatchlist: publicProcedure
    .input(z.object({ symbols: z.array(z.string()) }))
    .mutation(async ({ input }) => {
      try {
        await setRedisData("market:watchlist", input.symbols, 86400 * 30); // 30 days
        return { success: true };
      } catch (error) {
        console.error("Failed to update watchlist:", error);
        throw error;
      }
    }),
});
