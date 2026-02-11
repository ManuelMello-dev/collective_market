import { useState } from "react";
import { trpc } from "@/lib/trpc";
import DashboardNav from "@/components/DashboardNav";

interface AlertRule {
  id: number;
  name: string;
  type: "circuit_breaker" | "drawdown" | "error_rate" | "latency";
  threshold: number;
  isActive: boolean;
}

export default function Alerts() {
  const [alertRules, setAlertRules] = useState<AlertRule[]>([
    {
      id: 1,
      name: "Portfolio Drawdown Limit",
      type: "drawdown",
      threshold: 0.1,
      isActive: true,
    },
    {
      id: 2,
      name: "Error Rate Threshold",
      type: "error_rate",
      threshold: 0.05,
      isActive: true,
    },
    {
      id: 3,
      name: "Service Latency Limit",
      type: "latency",
      threshold: 500,
      isActive: true,
    },
    {
      id: 4,
      name: "Circuit Breaker - Sim Engine",
      type: "circuit_breaker",
      threshold: 3,
      isActive: false,
    },
  ]);

  const [activeAlerts, setActiveAlerts] = useState([
    {
      id: 1,
      rule: "Portfolio Drawdown Limit",
      severity: "warning",
      message: "Portfolio down 8.5% from peak",
      timestamp: new Date(Date.now() - 300000),
    },
    {
      id: 2,
      rule: "Service Latency Limit",
      severity: "error",
      message: "InfluxDB latency exceeded 5000ms",
      timestamp: new Date(Date.now() - 120000),
    },
  ]);

  const getAlertTypeColor = (type: string) => {
    switch (type) {
      case "circuit_breaker":
        return "text-red-600";
      case "drawdown":
        return "text-yellow-600";
      case "error_rate":
        return "text-orange-600";
      case "latency":
        return "text-blue-600";
      default:
        return "text-foreground";
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "error":
        return "bg-red-600";
      case "warning":
        return "bg-yellow-600";
      case "info":
        return "bg-blue-600";
      default:
        return "bg-gray-600";
    }
  };

  return (
    <div className="flex">
      <DashboardNav />

      <main className="ml-64 flex-1 bg-white">
        {/* Header */}
        <div className="border-b-4 border-foreground p-12">
          <h1 className="text-display">ALERT MANAGEMENT</h1>
          <p className="text-mono text-sm mt-4 text-muted">
            Circuit breakers • Drawdown limits • Error thresholds
          </p>
        </div>

        {/* Active Alerts */}
        <div className="p-12 border-b-4 border-foreground">
          <h2 className="text-headline mb-8">
            ACTIVE ALERTS ({activeAlerts.length})
          </h2>

          {activeAlerts.length > 0 ? (
            <div className="space-y-4">
              {activeAlerts.map((alert) => (
                <div
                  key={alert.id}
                  className={`card-brutalist border-l-8 ${getSeverityColor(alert.severity)}`}
                >
                  <div className="grid grid-cols-5 gap-8 items-center">
                    <div>
                      <div className="text-xs font-mono tracking-widest text-muted mb-2">
                        RULE
                      </div>
                      <div className="font-bold">{alert.rule}</div>
                    </div>

                    <div>
                      <div className="text-xs font-mono tracking-widest text-muted mb-2">
                        SEVERITY
                      </div>
                      <div className="font-bold uppercase text-sm">
                        {alert.severity}
                      </div>
                    </div>

                    <div className="col-span-2">
                      <div className="text-xs font-mono tracking-widest text-muted mb-2">
                        MESSAGE
                      </div>
                      <div className="font-mono text-sm">{alert.message}</div>
                    </div>

                    <div>
                      <div className="text-xs font-mono tracking-widest text-muted mb-2">
                        TIME
                      </div>
                      <div className="text-sm font-mono">
                        {alert.timestamp.toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="card-brutalist text-center py-12">
              <p className="text-2xl font-bold">NO ACTIVE ALERTS</p>
              <p className="text-muted mt-2">All systems operating normally</p>
            </div>
          )}
        </div>

        {/* Alert Rules */}
        <div className="p-12">
          <h2 className="text-headline mb-8">ALERT RULES ({alertRules.length})</h2>

          <div className="space-y-4">
            {alertRules.map((rule) => (
              <div key={rule.id} className="card-brutalist">
                <div className="grid grid-cols-6 gap-8 items-center">
                  <div>
                    <div className="text-xs font-mono tracking-widest text-muted mb-2">
                      RULE NAME
                    </div>
                    <div className="font-bold">{rule.name}</div>
                  </div>

                  <div>
                    <div className="text-xs font-mono tracking-widest text-muted mb-2">
                      TYPE
                    </div>
                    <div className={`font-bold uppercase text-sm ${getAlertTypeColor(rule.type)}`}>
                      {rule.type.replace("_", " ")}
                    </div>
                  </div>

                  <div>
                    <div className="text-xs font-mono tracking-widest text-muted mb-2">
                      THRESHOLD
                    </div>
                    <div className="font-bold">
                      {rule.type === "drawdown"
                        ? `${(rule.threshold * 100).toFixed(1)}%`
                        : rule.type === "error_rate"
                          ? `${(rule.threshold * 100).toFixed(2)}%`
                          : rule.type === "latency"
                            ? `${rule.threshold}ms`
                            : rule.threshold}
                    </div>
                  </div>

                  <div>
                    <div className="text-xs font-mono tracking-widest text-muted mb-2">
                      STATUS
                    </div>
                    <div className="flex items-center gap-2">
                      <div
                        className={`w-3 h-3 ${
                          rule.isActive ? "bg-green-600" : "bg-gray-400"
                        }`}
                      />
                      <span className="font-bold">
                        {rule.isActive ? "ACTIVE" : "INACTIVE"}
                      </span>
                    </div>
                  </div>

                  <div>
                    <button className="px-4 py-2 font-bold text-xs tracking-wider border-2 border-foreground hover:bg-foreground hover:text-background transition-colors">
                      EDIT
                    </button>
                  </div>

                  <div>
                    <button className="px-4 py-2 font-bold text-xs tracking-wider border-2 border-red-600 text-red-600 hover:bg-red-600 hover:text-white transition-colors">
                      DELETE
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Create New Rule */}
          <div className="mt-12 card-brutalist">
            <h3 className="text-title mb-8">CREATE NEW ALERT RULE</h3>

            <div className="grid grid-cols-2 gap-8">
              <div>
                <label className="block text-xs font-mono tracking-widest text-muted mb-2">
                  RULE NAME
                </label>
                <input
                  type="text"
                  placeholder="Enter rule name"
                  className="input-brutalist"
                />
              </div>

              <div>
                <label className="block text-xs font-mono tracking-widest text-muted mb-2">
                  TYPE
                </label>
                <select className="input-brutalist">
                  <option>circuit_breaker</option>
                  <option>drawdown</option>
                  <option>error_rate</option>
                  <option>latency</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-mono tracking-widest text-muted mb-2">
                  THRESHOLD
                </label>
                <input
                  type="number"
                  placeholder="0.1"
                  className="input-brutalist"
                />
              </div>

              <div className="flex items-end">
                <button className="w-full px-8 py-3 font-bold text-sm tracking-wider border-3 border-foreground hover:bg-foreground hover:text-background transition-colors">
                  CREATE RULE
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
