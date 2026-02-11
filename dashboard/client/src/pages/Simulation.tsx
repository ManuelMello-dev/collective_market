import { useState } from "react";
import { trpc } from "@/lib/trpc";
import DashboardNav from "@/components/DashboardNav";

export default function Simulation() {
  const [globalState, setGlobalState] = useState({
    step: 1250,
    globalState: 0.8745,
    activeSignals: 23,
    agentPrices: { agent_1: 145.2, agent_2: 142.8, agent_3: 148.5 },
    recordedAt: new Date(),
  });

  const { data: simData } = trpc.simulation.getGlobalState.useQuery();

  return (
    <div className="flex">
      <DashboardNav />

      <main className="ml-64 flex-1 bg-white">
        {/* Header */}
        <div className="border-b-4 border-foreground p-12">
          <h1 className="text-display">SIMULATION ENGINE</h1>
          <p className="text-mono text-sm mt-4 text-muted">
            Global state (Z³) • Agent dynamics • Signal generation
          </p>
        </div>

        {/* Global State Overview */}
        <div className="grid grid-cols-3 gap-8 p-12 border-b-4 border-foreground">
          <div className="card-brutalist">
            <div className="text-xs font-mono tracking-widest text-muted mb-4">
              SIMULATION STEP
            </div>
            <div className="text-6xl font-black">{globalState.step}</div>
            <div className="text-xs font-mono mt-4 text-muted">
              Iterations executed
            </div>
          </div>

          <div className="card-brutalist">
            <div className="text-xs font-mono tracking-widest text-muted mb-4">
              GLOBAL STATE (Z³)
            </div>
            <div className="text-6xl font-black text-green-600">
              {globalState.globalState.toFixed(4)}
            </div>
            <div className="mt-4 h-3 bg-muted">
              <div
                className="h-full bg-green-600"
                style={{ width: `${globalState.globalState * 100}%` }}
              />
            </div>
          </div>

          <div className="card-brutalist">
            <div className="text-xs font-mono tracking-widest text-muted mb-4">
              ACTIVE SIGNALS
            </div>
            <div className="text-6xl font-black text-blue-600">
              {globalState.activeSignals}
            </div>
            <div className="text-xs font-mono mt-4 text-muted">
              Agents generating signals
            </div>
          </div>
        </div>

        {/* Agent Prices */}
        <div className="p-12 border-b-4 border-foreground">
          <h2 className="text-headline mb-8">AGENT PRICE ESTIMATES</h2>

          <div className="grid grid-cols-3 gap-8">
            {Object.entries(globalState.agentPrices).map(([agent, price]) => (
              <div key={agent} className="card-brutalist">
                <div className="text-xs font-mono tracking-widest text-muted mb-4">
                  {agent.toUpperCase()}
                </div>
                <div className="text-5xl font-black">${price.toFixed(2)}</div>
                <div className="mt-4 text-xs font-mono text-muted">
                  Agent valuation
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Simulation Metrics */}
        <div className="p-12">
          <h2 className="text-headline mb-8">SIMULATION METRICS</h2>

          <div className="grid grid-cols-2 gap-8">
            <div className="card-brutalist">
              <div className="text-xs font-mono tracking-widest text-muted mb-4">
                CONVERGENCE RATE
              </div>
              <div className="text-4xl font-black">0.0234</div>
              <div className="mt-4 h-2 bg-muted">
                <div className="h-full w-1/3 bg-foreground" />
              </div>
              <div className="text-xs font-mono mt-2 text-muted">
                Change per step
              </div>
            </div>

            <div className="card-brutalist">
              <div className="text-xs font-mono tracking-widest text-muted mb-4">
                VOLATILITY INDEX
              </div>
              <div className="text-4xl font-black">0.1245</div>
              <div className="mt-4 h-2 bg-muted">
                <div className="h-full w-1/4 bg-yellow-600" />
              </div>
              <div className="text-xs font-mono mt-2 text-muted">
                Market volatility
              </div>
            </div>

            <div className="card-brutalist">
              <div className="text-xs font-mono tracking-widest text-muted mb-4">
                AGENT CONSENSUS
              </div>
              <div className="text-4xl font-black">0.8234</div>
              <div className="mt-4 h-2 bg-muted">
                <div className="h-full w-4/5 bg-green-600" />
              </div>
              <div className="text-xs font-mono mt-2 text-muted">
                Agreement level
              </div>
            </div>

            <div className="card-brutalist">
              <div className="text-xs font-mono tracking-widest text-muted mb-4">
                SIGNAL QUALITY
              </div>
              <div className="text-4xl font-black">0.7456</div>
              <div className="mt-4 h-2 bg-muted">
                <div className="h-full w-3/4 bg-blue-600" />
              </div>
              <div className="text-xs font-mono mt-2 text-muted">
                Signal confidence
              </div>
            </div>
          </div>
        </div>

        {/* State History */}
        <div className="p-12 border-t-4 border-foreground">
          <h2 className="text-headline mb-8">STATE EVOLUTION</h2>

          <div className="card-brutalist">
            <div className="text-xs font-mono tracking-widest text-muted mb-4">
              GLOBAL STATE HISTORY
            </div>
            <div className="h-48 bg-muted flex items-end gap-1 p-4">
              {[0.2, 0.3, 0.45, 0.52, 0.61, 0.68, 0.72, 0.78, 0.82, 0.85].map(
                (height, i) => (
                  <div
                    key={i}
                    className="flex-1 bg-green-600"
                    style={{ height: `${height * 100}%` }}
                  />
                )
              )}
            </div>
            <div className="text-xs font-mono mt-4 text-muted">
              Last 10 steps
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
