import { useState, useEffect } from "react";
import { trpc } from "@/lib/trpc";
import DashboardNav from "@/components/DashboardNav";

interface MarketSymbol {
  symbol: string;
  price: number;
  volume: number;
  sentiment: number | null;
  change: number;
}

export default function Market() {
  const [symbols, setSymbols] = useState<MarketSymbol[]>([
    { symbol: "AAPL", price: 150.25, volume: 2500000, sentiment: 0.65, change: 2.5 },
    { symbol: "MSFT", price: 380.15, volume: 1800000, sentiment: 0.72, change: 1.8 },
    { symbol: "GOOGL", price: 140.85, volume: 1200000, sentiment: 0.68, change: 3.2 },
    { symbol: "AMZN", price: 180.45, volume: 2100000, sentiment: 0.61, change: -0.5 },
    { symbol: "NVDA", price: 875.30, volume: 3200000, sentiment: 0.78, change: 5.1 },
  ]);

  const [sentiment, setSentiment] = useState({ equity: 0.65, crypto: 0.58 });
  const [selectedSymbol, setSelectedSymbol] = useState<string | null>(null);

  // Fetch market sentiment
  const { data: sentimentData } = trpc.market.getMarketSentiment.useQuery();

  useEffect(() => {
    if (sentimentData) {
      setSentiment(sentimentData as typeof sentiment);
    }
  }, [sentimentData]);

  const getSentimentColor = (value: number) => {
    if (value > 0.7) return "text-green-600";
    if (value > 0.5) return "text-yellow-600";
    return "text-red-600";
  };

  const getChangeColor = (change: number) => {
    return change >= 0 ? "text-green-600" : "text-red-600";
  };

  return (
    <div className="flex">
      <DashboardNav />

      <main className="ml-64 flex-1 bg-white">
        {/* Header */}
        <div className="border-b-4 border-foreground p-12">
          <h1 className="text-display">MARKET INTELLIGENCE</h1>
          <p className="text-mono text-sm mt-4 text-muted">
            Real-time price monitoring • Sentiment analysis • Volume tracking
          </p>
        </div>

        {/* Sentiment Overview */}
        <div className="grid grid-cols-2 gap-8 p-12 border-b-4 border-foreground">
          <div className="card-brutalist">
            <div className="text-xs font-mono tracking-widest text-muted mb-4">
              EQUITY SENTIMENT
            </div>
            <div className={`text-6xl font-black tracking-tighter ${getSentimentColor(sentiment.equity)}`}>
              {(sentiment.equity * 100).toFixed(0)}%
            </div>
            <div className="mt-4 h-2 bg-muted">
              <div
                className="h-full bg-foreground"
                style={{ width: `${sentiment.equity * 100}%` }}
              />
            </div>
          </div>

          <div className="card-brutalist">
            <div className="text-xs font-mono tracking-widest text-muted mb-4">
              CRYPTO SENTIMENT
            </div>
            <div className={`text-6xl font-black tracking-tighter ${getSentimentColor(sentiment.crypto)}`}>
              {(sentiment.crypto * 100).toFixed(0)}%
            </div>
            <div className="mt-4 h-2 bg-muted">
              <div
                className="h-full bg-foreground"
                style={{ width: `${sentiment.crypto * 100}%` }}
              />
            </div>
          </div>
        </div>

        {/* Market Data Grid */}
        <div className="p-12">
          <h2 className="text-headline mb-8">TRACKED SYMBOLS</h2>

          <div className="grid grid-cols-1 gap-4">
            {symbols.map((symbol) => (
              <div
                key={symbol.symbol}
                onClick={() => setSelectedSymbol(symbol.symbol)}
                className={`card-brutalist cursor-pointer transition-all ${
                  selectedSymbol === symbol.symbol ? "bg-foreground text-background" : ""
                }`}
              >
                <div className="grid grid-cols-5 gap-8">
                  <div>
                    <div className="text-xs font-mono tracking-widest opacity-70 mb-2">
                      SYMBOL
                    </div>
                    <div className="text-3xl font-black">{symbol.symbol}</div>
                  </div>

                  <div>
                    <div className="text-xs font-mono tracking-widest opacity-70 mb-2">
                      PRICE
                    </div>
                    <div className="text-3xl font-black">${symbol.price.toFixed(2)}</div>
                  </div>

                  <div>
                    <div className="text-xs font-mono tracking-widest opacity-70 mb-2">
                      VOLUME
                    </div>
                    <div className="text-lg font-bold">
                      {(symbol.volume / 1000000).toFixed(1)}M
                    </div>
                  </div>

                  <div>
                    <div className="text-xs font-mono tracking-widest opacity-70 mb-2">
                      SENTIMENT
                    </div>
                    <div className={`text-2xl font-black ${getSentimentColor(symbol.sentiment || 0.5)}`}>
                      {((symbol.sentiment || 0.5) * 100).toFixed(0)}%
                    </div>
                  </div>

                  <div>
                    <div className="text-xs font-mono tracking-widest opacity-70 mb-2">
                      CHANGE
                    </div>
                    <div className={`text-2xl font-black ${getChangeColor(symbol.change)}`}>
                      {symbol.change > 0 ? "+" : ""}{symbol.change.toFixed(2)}%
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Volume Analysis */}
        {selectedSymbol && (
          <div className="p-12 border-t-4 border-foreground">
            <h2 className="text-headline mb-8">ATTENTION ANALYSIS: {selectedSymbol}</h2>

            <div className="grid grid-cols-3 gap-8">
              <div className="card-brutalist">
                <div className="text-xs font-mono tracking-widest text-muted mb-4">
                  CURRENT VOLUME
                </div>
                <div className="text-5xl font-black">2.5M</div>
              </div>

              <div className="card-brutalist">
                <div className="text-xs font-mono tracking-widest text-muted mb-4">
                  AVG VOLUME
                </div>
                <div className="text-5xl font-black">1.8M</div>
              </div>

              <div className="card-brutalist">
                <div className="text-xs font-mono tracking-widest text-muted mb-4">
                  VOLUME RATIO
                </div>
                <div className="text-5xl font-black text-green-600">1.39x</div>
              </div>
            </div>

            <div className="mt-8 card-brutalist">
              <div className="text-xs font-mono tracking-widest text-muted mb-4">
                VOLUME TREND
              </div>
              <div className="h-32 bg-muted flex items-end gap-1 p-4">
                {[0.4, 0.6, 0.8, 0.5, 0.9, 0.7, 1.0, 0.8, 0.6, 0.9].map((height, i) => (
                  <div
                    key={i}
                    className="flex-1 bg-foreground"
                    style={{ height: `${height * 100}%` }}
                  />
                ))}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
