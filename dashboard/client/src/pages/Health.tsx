import { useState } from "react";
import { trpc } from "@/lib/trpc";
import DashboardNav from "@/components/DashboardNav";

interface ServiceStatus {
  service: string;
  isHealthy: boolean;
  latencyMs: number | null;
  errorCount: number;
  lastError: string | null;
}

export default function Health() {
  const [services, setServices] = useState<ServiceStatus[]>([
    {
      service: "ingestion",
      isHealthy: true,
      latencyMs: 45.2,
      errorCount: 0,
      lastError: null,
    },
    {
      service: "memory_hub",
      isHealthy: true,
      latencyMs: 12.8,
      errorCount: 0,
      lastError: null,
    },
    {
      service: "sim_engine",
      isHealthy: true,
      latencyMs: 234.5,
      errorCount: 0,
      lastError: null,
    },
    {
      service: "redis",
      isHealthy: true,
      latencyMs: 2.3,
      errorCount: 0,
      lastError: null,
    },
    {
      service: "mysql",
      isHealthy: true,
      latencyMs: 8.5,
      errorCount: 0,
      lastError: null,
    },
    {
      service: "influxdb",
      isHealthy: false,
      latencyMs: 5000,
      errorCount: 3,
      lastError: "Connection timeout",
    },
  ]);

  const { data: healthData } = trpc.health.getSystemHealth.useQuery();

  const healthyCount = services.filter((s) => s.isHealthy).length;
  const totalCount = services.length;

  return (
    <div className="flex">
      <DashboardNav />

      <main className="ml-64 flex-1 bg-white">
        {/* Header */}
        <div className="border-b-4 border-foreground p-12">
          <h1 className="text-display">SYSTEM HEALTH</h1>
          <p className="text-mono text-sm mt-4 text-muted">
            Microservices status • Latency monitoring • Error tracking
          </p>
        </div>

        {/* Overall Health */}
        <div className="grid grid-cols-3 gap-8 p-12 border-b-4 border-foreground">
          <div className="card-brutalist">
            <div className="text-xs font-mono tracking-widest text-muted mb-4">
              SERVICES ONLINE
            </div>
            <div className="text-6xl font-black text-green-600">
              {healthyCount}/{totalCount}
            </div>
            <div className="mt-4 h-3 bg-muted">
              <div
                className="h-full bg-green-600"
                style={{ width: `${(healthyCount / totalCount) * 100}%` }}
              />
            </div>
          </div>

          <div className="card-brutalist">
            <div className="text-xs font-mono tracking-widest text-muted mb-4">
              TOTAL ERRORS
            </div>
            <div className="text-6xl font-black text-red-600">
              {services.reduce((sum, s) => sum + s.errorCount, 0)}
            </div>
            <div className="text-xs font-mono mt-4 text-muted">
              Across all services
            </div>
          </div>

          <div className="card-brutalist">
            <div className="text-xs font-mono tracking-widest text-muted mb-4">
              AVG LATENCY
            </div>
            <div className="text-6xl font-black">
              {(
                services.reduce((sum, s) => sum + (s.latencyMs || 0), 0) /
                services.length
              ).toFixed(1)}ms
            </div>
            <div className="text-xs font-mono mt-4 text-muted">
              Response time
            </div>
          </div>
        </div>

        {/* Service Status Table */}
        <div className="p-12">
          <h2 className="text-headline mb-8">MICROSERVICES STATUS</h2>

          <div className="space-y-4">
            {services.map((service) => (
              <div
                key={service.service}
                className={`card-brutalist ${
                  !service.isHealthy ? "border-red-600" : ""
                }`}
              >
                <div className="grid grid-cols-6 gap-8 items-center">
                  <div>
                    <div className="text-xs font-mono tracking-widest text-muted mb-2">
                      SERVICE
                    </div>
                    <div className="text-2xl font-bold">
                      {service.service.toUpperCase()}
                    </div>
                  </div>

                  <div>
                    <div className="text-xs font-mono tracking-widest text-muted mb-2">
                      STATUS
                    </div>
                    <div className="flex items-center gap-2">
                      <div
                        className={`w-4 h-4 ${
                          service.isHealthy
                            ? "bg-green-600"
                            : "bg-red-600 animate-pulse"
                        }`}
                      />
                      <span className="font-bold">
                        {service.isHealthy ? "ONLINE" : "OFFLINE"}
                      </span>
                    </div>
                  </div>

                  <div>
                    <div className="text-xs font-mono tracking-widest text-muted mb-2">
                      LATENCY
                    </div>
                    <div className="text-lg font-bold">
                      {service.latencyMs?.toFixed(1)}ms
                    </div>
                  </div>

                  <div>
                    <div className="text-xs font-mono tracking-widest text-muted mb-2">
                      ERRORS
                    </div>
                    <div
                      className={`text-lg font-bold ${
                        service.errorCount > 0 ? "text-red-600" : "text-green-600"
                      }`}
                    >
                      {service.errorCount}
                    </div>
                  </div>

                  <div>
                    <div className="text-xs font-mono tracking-widest text-muted mb-2">
                      LAST ERROR
                    </div>
                    <div className="text-sm font-mono">
                      {service.lastError || "—"}
                    </div>
                  </div>

                  <div>
                    <button className="px-4 py-2 font-bold text-xs tracking-wider border-2 border-foreground hover:bg-foreground hover:text-background transition-colors">
                      RESTART
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="p-12 border-t-4 border-foreground">
          <h2 className="text-headline mb-8">PERFORMANCE METRICS</h2>

          <div className="grid grid-cols-2 gap-8">
            <div className="card-brutalist">
              <div className="text-xs font-mono tracking-widest text-muted mb-4">
                LATENCY DISTRIBUTION
              </div>
              <div className="space-y-2">
                <div className="flex items-center gap-4">
                  <span className="w-20 text-xs font-mono">0-10ms</span>
                  <div className="flex-1 h-2 bg-muted">
                    <div className="h-full w-1/2 bg-green-600" />
                  </div>
                  <span className="text-xs font-mono">50%</span>
                </div>
                <div className="flex items-center gap-4">
                  <span className="w-20 text-xs font-mono">10-50ms</span>
                  <div className="flex-1 h-2 bg-muted">
                    <div className="h-full w-1/3 bg-yellow-600" />
                  </div>
                  <span className="text-xs font-mono">33%</span>
                </div>
                <div className="flex items-center gap-4">
                  <span className="w-20 text-xs font-mono">50ms+</span>
                  <div className="flex-1 h-2 bg-muted">
                    <div className="h-full w-1/6 bg-red-600" />
                  </div>
                  <span className="text-xs font-mono">17%</span>
                </div>
              </div>
            </div>

            <div className="card-brutalist">
              <div className="text-xs font-mono tracking-widest text-muted mb-4">
                ERROR RATE TREND
              </div>
              <div className="h-32 bg-muted flex items-end gap-1 p-4">
                {[0.1, 0.05, 0.08, 0.03, 0.02, 0.01, 0.0, 0.0, 0.0, 0.0].map(
                  (height, i) => (
                    <div
                      key={i}
                      className={`flex-1 ${height > 0 ? "bg-red-600" : "bg-green-600"}`}
                      style={{ height: `${Math.max(height * 100, 2)}%` }}
                    />
                  )
                )}
              </div>
              <div className="text-xs font-mono mt-4 text-muted">
                Last 10 minutes
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
