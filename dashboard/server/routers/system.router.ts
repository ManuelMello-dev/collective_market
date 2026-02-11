import { z } from "zod";
import { publicProcedure, router } from "../_core/trpc";
import * as db from "../market.db";
import { getSystemHealth, getRedisData, setRedisData } from "../integrations";

export const simulationRouter = router({
  // Get latest simulation global state (Z³)
  getGlobalState: publicProcedure.query(async () => {
    try {
      const state = await db.getLatestSimulationState();
      if (!state) {
        return {
          step: 0,
          globalState: 0,
          activeSignals: 0,
          agentPrices: {},
          recordedAt: new Date(),
        };
      }

      return {
        step: state.step,
        globalState: parseFloat(state.globalState as unknown as string),
        activeSignals: state.activeSignals,
        agentPrices: state.agentPrices ? JSON.parse(state.agentPrices as unknown as string) : {},
        recordedAt: state.recordedAt,
      };
    } catch (error) {
      console.error("Failed to get global state:", error);
      throw error;
    }
  }),

  // Get active signals
  getActiveSignals: publicProcedure.query(async () => {
    try {
      const signals = await db.getLatestSignals(20);
      return signals.map((s) => ({
        symbol: s.symbol,
        signal: s.signal,
        confidence: parseFloat(s.confidence as unknown as string),
        price: parseFloat(s.price as unknown as string),
        reason: s.reason,
        generatedAt: s.generatedAt,
      }));
    } catch (error) {
      console.error("Failed to get active signals:", error);
      throw error;
    }
  }),

  // Record simulation state
  recordState: publicProcedure
    .input(
      z.object({
        step: z.number(),
        globalState: z.number(),
        activeSignals: z.number(),
        agentPrices: z.record(z.string(), z.number()).optional(),
      })
    )
    .mutation(async ({ input }) => {
      try {
        await db.recordSimulationState(
          input.step,
          input.globalState,
          input.activeSignals,
          input.agentPrices || null
        );

        // Cache in Redis
        await setRedisData(
          "simulation:latest",
          {
            step: input.step,
            globalState: input.globalState,
            activeSignals: input.activeSignals,
            timestamp: new Date(),
          },
          3600
        );

        return { success: true };
      } catch (error) {
        console.error("Failed to record simulation state:", error);
        throw error;
      }
    }),
});

export const healthRouter = router({
  // Get system health overview
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

  // Get service status
  getServiceStatus: publicProcedure
    .input(z.object({ service: z.string() }))
    .query(async ({ input }) => {
      try {
        const health = await db.getServiceHealth(input.service);
        if (!health) {
          return {
            service: input.service,
            isHealthy: false,
            latencyMs: null,
            errorCount: 0,
            lastError: null,
            checkedAt: new Date(),
          };
        }

        return {
          service: health.service,
          isHealthy: health.isHealthy,
          latencyMs: health.latencyMs
            ? parseFloat(health.latencyMs as unknown as string)
            : null,
          errorCount: health.errorCount || 0,
          lastError: health.lastError,
          checkedAt: health.checkedAt,
        };
      } catch (error) {
        console.error("Failed to get service status:", error);
        throw error;
      }
    }),

  // Get all services health
  getAllServicesHealth: publicProcedure.query(async () => {
    try {
      const services = await db.getAllServicesHealth();
      return services.map((s) => ({
        service: s.service,
        isHealthy: s.isHealthy,
        latencyMs: s.latencyMs
          ? parseFloat(s.latencyMs as unknown as string)
          : null,
        errorCount: s.errorCount || 0,
        lastError: s.lastError,
        checkedAt: s.checkedAt,
      }));
    } catch (error) {
      console.error("Failed to get all services health:", error);
      throw error;
    }
  }),

  // Record service health
  recordServiceHealth: publicProcedure
    .input(
      z.object({
        service: z.string(),
        isHealthy: z.boolean(),
        latencyMs: z.number().optional(),
        errorCount: z.number().optional(),
        lastError: z.string().optional(),
      })
    )
    .mutation(async ({ input }) => {
      try {
        await db.recordServiceHealth(
          input.service,
          input.isHealthy,
          input.latencyMs || null,
          input.errorCount || 0,
          input.lastError || null
        );

        return { success: true };
      } catch (error) {
        console.error("Failed to record service health:", error);
        throw error;
      }
    }),

  // Get system metrics
  getSystemMetrics: publicProcedure.query(async () => {
    try {
      const health = await getSystemHealth();
      const services = await db.getAllServicesHealth();

      return {
        health,
        services: services.map((s) => ({
          service: s.service,
          isHealthy: s.isHealthy,
          latencyMs: s.latencyMs
            ? parseFloat(s.latencyMs as unknown as string)
            : null,
          errorCount: s.errorCount || 0,
        })),
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      console.error("Failed to get system metrics:", error);
      throw error;
    }
  }),
});

export const alertRouter = router({
  // Get alert rules
  getAlertRules: publicProcedure.query(async () => {
    try {
      const rules = await db.getAlertRules();
      return rules.map((r) => ({
        id: r.id,
        name: r.name,
        type: r.type,
        threshold: parseFloat(r.threshold as unknown as string),
        isActive: r.isActive,
        metadata: r.metadata ? JSON.parse(r.metadata as unknown as string) : null,
        createdAt: r.createdAt,
        updatedAt: r.updatedAt,
      }));
    } catch (error) {
      console.error("Failed to get alert rules:", error);
      throw error;
    }
  }),

  // Get active alert rules
  getActiveAlertRules: publicProcedure.query(async () => {
    try {
      const rules = await db.getActiveAlertRules();
      return rules.map((r) => ({
        id: r.id,
        name: r.name,
        type: r.type,
        threshold: parseFloat(r.threshold as unknown as string),
        metadata: r.metadata ? JSON.parse(r.metadata as unknown as string) : null,
      }));
    } catch (error) {
      console.error("Failed to get active alert rules:", error);
      throw error;
    }
  }),

  // Create alert rule
  createAlertRule: publicProcedure
    .input(
      z.object({
        name: z.string(),
        type: z.enum(["circuit_breaker", "drawdown", "error_rate", "latency"]),
        threshold: z.number(),
        metadata: z.record(z.string(), z.unknown()).optional(),
      })
    )
    .mutation(async ({ input }) => {
      try {
        await db.createAlertRule(
          input.name,
          input.type,
          input.threshold,
          (input.metadata as Record<string, unknown>) || null
        );

        return { success: true };
      } catch (error) {
        console.error("Failed to create alert rule:", error);
        throw error;
      }
    }),

  // Update alert rule
  updateAlertRule: publicProcedure
    .input(
      z.object({
        id: z.number(),
        isActive: z.boolean(),
        threshold: z.number().optional(),
      })
    )
    .mutation(async ({ input }) => {
      try {
        await db.updateAlertRule(input.id, input.isActive, input.threshold || null);
        return { success: true };
      } catch (error) {
        console.error("Failed to update alert rule:", error);
        throw error;
      }
    }),
});
