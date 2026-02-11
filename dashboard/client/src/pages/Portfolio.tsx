import { useState, useEffect } from "react";
import { trpc } from "@/lib/trpc";
import DashboardNav from "@/components/DashboardNav";

interface Position {
  symbol: string;
  quantity: number;
  entryPrice: number;
  currentPrice: number;
  unrealizedPnl: number;
  pnlPercent: number;
}

export default function Portfolio() {
  const [positions, setPositions] = useState<Position[]>([
    {
      symbol: "AAPL",
      quantity: 100,
      entryPrice: 145.0,
      currentPrice: 150.25,
      unrealizedPnl: 525.0,
      pnlPercent: 3.62,
    },
    {
      symbol: "MSFT",
      quantity: 50,
      entryPrice: 375.0,
      currentPrice: 380.15,
      unrealizedPnl: 257.5,
      pnlPercent: 1.37,
    },
    {
      symbol: "NVDA",
      quantity: 20,
      entryPrice: 850.0,
      currentPrice: 875.3,
      unrealizedPnl: 506.0,
      pnlPercent: 2.98,
    },
  ]);

  const [portfolioState, setPortfolioState] = useState({
    totalValue: 125288.5,
    capital: 50000,
    closedPnl: 2500,
    unrealizedPnl: 1288.5,
    positionsCount: 3,
    sharpeRatio: 1.85,
    maxDrawdown: -0.045,
    winRate: 0.68,
  });

  // Fetch portfolio data
  const { data: portfolioData } = trpc.portfolio.getPortfolioState.useQuery();

  useEffect(() => {
    if (portfolioData) {
      setPortfolioState(portfolioData as typeof portfolioState);
    }
  }, [portfolioData]);

  const totalPnl = portfolioState.closedPnl + portfolioState.unrealizedPnl;
  const returnPct = (totalPnl / 100000) * 100;

  return (
    <div className="flex">
      <DashboardNav />

      <main className="ml-64 flex-1 bg-white">
        {/* Header */}
        <div className="border-b-4 border-foreground p-12">
          <h1 className="text-display">PORTFOLIO PERFORMANCE</h1>
          <p className="text-mono text-sm mt-4 text-muted">
            Position management • P&L tracking • Risk metrics
          </p>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-4 gap-8 p-12 border-b-4 border-foreground">
          <div className="card-brutalist">
            <div className="text-xs font-mono tracking-widest text-muted mb-4">
              TOTAL VALUE
            </div>
            <div className="text-4xl font-black">
              ${portfolioState.totalValue.toFixed(2)}
            </div>
            <div className="text-sm font-bold mt-4 text-green-600">
              +${totalPnl.toFixed(2)} ({returnPct.toFixed(2)}%)
            </div>
          </div>

          <div className="card-brutalist">
            <div className="text-xs font-mono tracking-widest text-muted mb-4">
              SHARPE RATIO
            </div>
            <div className="text-4xl font-black">{portfolioState.sharpeRatio.toFixed(2)}</div>
            <div className="text-xs font-mono mt-4 text-muted">Risk-adjusted return</div>
          </div>

          <div className="card-brutalist">
            <div className="text-xs font-mono tracking-widest text-muted mb-4">
              MAX DRAWDOWN
            </div>
            <div className="text-4xl font-black text-red-600">
              {(portfolioState.maxDrawdown * 100).toFixed(2)}%
            </div>
            <div className="text-xs font-mono mt-4 text-muted">Largest decline</div>
          </div>

          <div className="card-brutalist">
            <div className="text-xs font-mono tracking-widest text-muted mb-4">
              WIN RATE
            </div>
            <div className="text-4xl font-black text-green-600">
              {(portfolioState.winRate * 100).toFixed(0)}%
            </div>
            <div className="text-xs font-mono mt-4 text-muted">Winning trades</div>
          </div>
        </div>

        {/* P&L Breakdown */}
        <div className="grid grid-cols-2 gap-8 p-12 border-b-4 border-foreground">
          <div className="card-brutalist">
            <div className="text-xs font-mono tracking-widest text-muted mb-4">
              CLOSED P&L
            </div>
            <div className={`text-4xl font-black ${portfolioState.closedPnl >= 0 ? "text-green-600" : "text-red-600"}`}>
              ${portfolioState.closedPnl.toFixed(2)}
            </div>
            <div className="text-sm font-mono mt-4 text-muted">Realized gains/losses</div>
          </div>

          <div className="card-brutalist">
            <div className="text-xs font-mono tracking-widest text-muted mb-4">
              UNREALIZED P&L
            </div>
            <div className={`text-4xl font-black ${portfolioState.unrealizedPnl >= 0 ? "text-green-600" : "text-red-600"}`}>
              ${portfolioState.unrealizedPnl.toFixed(2)}
            </div>
            <div className="text-sm font-mono mt-4 text-muted">Open positions</div>
          </div>
        </div>

        {/* Open Positions */}
        <div className="p-12">
          <h2 className="text-headline mb-8">OPEN POSITIONS ({positions.length})</h2>

          <div className="overflow-x-auto">
            <table className="table-brutalist">
              <thead>
                <tr>
                  <th>SYMBOL</th>
                  <th>QUANTITY</th>
                  <th>ENTRY PRICE</th>
                  <th>CURRENT PRICE</th>
                  <th>UNREALIZED P&L</th>
                  <th>RETURN %</th>
                </tr>
              </thead>
              <tbody>
                {positions.map((pos) => (
                  <tr key={pos.symbol}>
                    <td className="font-bold">{pos.symbol}</td>
                    <td>{pos.quantity}</td>
                    <td>${pos.entryPrice.toFixed(2)}</td>
                    <td className="font-bold">${pos.currentPrice.toFixed(2)}</td>
                    <td className={pos.unrealizedPnl >= 0 ? "text-green-600 font-bold" : "text-red-600 font-bold"}>
                      ${pos.unrealizedPnl.toFixed(2)}
                    </td>
                    <td className={pos.pnlPercent >= 0 ? "text-green-600 font-bold" : "text-red-600 font-bold"}>
                      {pos.pnlPercent > 0 ? "+" : ""}{pos.pnlPercent.toFixed(2)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Portfolio Allocation */}
        <div className="p-12 border-t-4 border-foreground">
          <h2 className="text-headline mb-8">CAPITAL ALLOCATION</h2>

          <div className="grid grid-cols-2 gap-8">
            <div className="card-brutalist">
              <div className="text-xs font-mono tracking-widest text-muted mb-4">
                DEPLOYED CAPITAL
              </div>
              <div className="text-4xl font-black">
                ${(portfolioState.totalValue - portfolioState.capital).toFixed(2)}
              </div>
              <div className="mt-4 h-3 bg-muted">
                <div
                  className="h-full bg-foreground"
                  style={{
                    width: `${((portfolioState.totalValue - portfolioState.capital) / portfolioState.totalValue) * 100}%`,
                  }}
                />
              </div>
              <div className="text-xs font-mono mt-2 text-muted">
                {(((portfolioState.totalValue - portfolioState.capital) / portfolioState.totalValue) * 100).toFixed(1)}% deployed
              </div>
            </div>

            <div className="card-brutalist">
              <div className="text-xs font-mono tracking-widest text-muted mb-4">
                AVAILABLE CASH
              </div>
              <div className="text-4xl font-black">${portfolioState.capital.toFixed(2)}</div>
              <div className="mt-4 h-3 bg-muted">
                <div
                  className="h-full bg-foreground"
                  style={{
                    width: `${(portfolioState.capital / portfolioState.totalValue) * 100}%`,
                  }}
                />
              </div>
              <div className="text-xs font-mono mt-2 text-muted">
                {((portfolioState.capital / portfolioState.totalValue) * 100).toFixed(1)}% available
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
