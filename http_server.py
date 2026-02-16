"""
HTTP Server for Market Consciousness Dashboards
Serves alongside ZeroMQ network on separate port
"""
import asyncio
import logging
import os
from aiohttp import web
import json

logger = logging.getLogger(__name__)

# HTML Templates for dashboards
INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Market Consciousness Hub</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #000;
            color: #fff;
            line-height: 1.6;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 4rem;
        }
        h1 {
            font-size: 4rem;
            font-weight: 900;
            margin-bottom: 2rem;
            letter-spacing: -2px;
            text-transform: uppercase;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-top: 3rem;
        }
        .card {
            border: 4px solid #fff;
            padding: 2rem;
            background: #111;
            transition: all 0.3s;
        }
        .card:hover {
            background: #222;
            transform: translate(-4px, -4px);
            box-shadow: 4px 4px 0 #fff;
        }
        .card h2 {
            font-size: 1.8rem;
            margin-bottom: 1rem;
            font-weight: 700;
        }
        .card p {
            font-size: 0.95rem;
            opacity: 0.8;
            margin-bottom: 1.5rem;
        }
        .btn {
            display: inline-block;
            background: #fff;
            color: #000;
            padding: 0.75rem 1.5rem;
            border: none;
            font-weight: 700;
            font-size: 0.9rem;
            cursor: pointer;
            text-decoration: none;
            transition: all 0.2s;
        }
        .btn:hover {
            background: #000;
            color: #fff;
            border: 2px solid #fff;
        }
        .status {
            margin-top: 3rem;
            padding: 2rem;
            border: 2px solid #666;
            background: #0a0a0a;
        }
        .status h3 {
            font-size: 1.3rem;
            margin-bottom: 1rem;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            padding: 0.5rem 0;
            border-bottom: 1px solid #333;
        }
        .metric-label {
            font-weight: 600;
        }
        .metric-value {
            color: #0f0;
            font-family: 'Courier New', monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>MARKET<br/>CONSCIOUSNESS</h1>
        
        <div class="grid">
            <div class="card">
                <h2>CONSCIOUSNESS DASHBOARD</h2>
                <p>Real-time cognitive mesh state, concept formation, and cross-domain transfers.</p>
                <a href="/dashboard" class="btn">ENTER</a>
            </div>
            
            <div class="card">
                <h2>EEG MONITOR</h2>
                <p>Neural activity visualization. Watch the cognitive mesh think.</p>
                <a href="/eeg" class="btn">ENTER</a>
            </div>
            
            <div class="card">
                <h2>SYSTEM STATUS</h2>
                <p>Health metrics, uptime, and operational statistics.</p>
                <a href="/status" class="btn">VIEW</a>
            </div>
        </div>
        
        <div class="status">
            <h3>SYSTEM METRICS</h3>
            <div id="metrics">
                <div class="metric">
                    <span class="metric-label">Status</span>
                    <span class="metric-value">ONLINE</span>
                </div>
                <div class="metric">
                    <span class="metric-label">ZeroMQ Network</span>
                    <span class="metric-value">ACTIVE</span>
                </div>
                <div class="metric">
                    <span class="metric-label">HTTP Server</span>
                    <span class="metric-value">RUNNING</span>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Market Consciousness Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #000;
            color: #fff;
        }
        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 2rem;
        }
        h1 {
            font-size: 3rem;
            font-weight: 900;
            margin-bottom: 2rem;
            text-transform: uppercase;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 1.5rem;
        }
        .panel {
            border: 3px solid #fff;
            padding: 1.5rem;
            background: #0a0a0a;
        }
        .panel h2 {
            font-size: 1.5rem;
            margin-bottom: 1rem;
            border-bottom: 2px solid #fff;
            padding-bottom: 0.5rem;
        }
        .stat {
            display: flex;
            justify-content: space-between;
            padding: 0.75rem 0;
            border-bottom: 1px solid #333;
        }
        .stat-label {
            font-weight: 600;
        }
        .stat-value {
            color: #0f0;
            font-family: 'Courier New', monospace;
            font-weight: 700;
        }
        .concept-list {
            margin-top: 1rem;
        }
        .concept-item {
            background: #111;
            padding: 0.75rem;
            margin: 0.5rem 0;
            border-left: 3px solid #0f0;
            font-size: 0.9rem;
        }
        .back-link {
            display: inline-block;
            margin-bottom: 2rem;
            color: #fff;
            text-decoration: none;
            border: 2px solid #fff;
            padding: 0.5rem 1rem;
            font-weight: 600;
        }
        .back-link:hover {
            background: #fff;
            color: #000;
        }
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-link">← HOME</a>
        
        <h1>CONSCIOUSNESS DASHBOARD</h1>
        
        <div class="grid">
            <div class="panel">
                <h2>COGNITIVE STATE</h2>
                <div class="stat">
                    <span class="stat-label">Concepts Formed</span>
                    <span class="stat-value" id="concepts">0</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Rules Learned</span>
                    <span class="stat-value" id="rules">0</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Transfers Made</span>
                    <span class="stat-value" id="transfers">0</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Goals Generated</span>
                    <span class="stat-value" id="goals">0</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Uptime (seconds)</span>
                    <span class="stat-value" id="uptime">0</span>
                </div>
            </div>
            
            <div class="panel">
                <h2>ACTIVE DOMAINS</h2>
                <div class="concept-list" id="domains">
                    <div class="concept-item">stock:AAPL</div>
                    <div class="concept-item">stock:MSFT</div>
                    <div class="concept-item">stock:GOOGL</div>
                    <div class="concept-item">stock:TSLA</div>
                    <div class="concept-item">stock:NVDA</div>
                    <div class="concept-item">crypto:BTC</div>
                    <div class="concept-item">crypto:ETH</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        async function updateMetrics() {
            try {
                const response = await fetch('/api/metrics');
                const data = await response.json();
                document.getElementById('concepts').textContent = data.concepts_formed || 0;
                document.getElementById('rules').textContent = data.rules_learned || 0;
                document.getElementById('transfers').textContent = data.transfers_made || 0;
                document.getElementById('goals').textContent = data.goals_generated || 0;
                document.getElementById('uptime').textContent = Math.floor(data.uptime_seconds || 0);
            } catch (e) {
                console.log('Metrics endpoint not available yet');
            }
        }
        
        updateMetrics();
        setInterval(updateMetrics, 2000);
    </script>
</body>
</html>
"""

EEG_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Market EEG Monitor</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #000;
            color: #0f0;
            overflow: hidden;
        }
        .container {
            width: 100vw;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        h1 {
            font-size: 2rem;
            padding: 1rem;
            border-bottom: 3px solid #0f0;
            text-transform: uppercase;
        }
        .eeg-container {
            flex: 1;
            padding: 1rem;
            overflow-y: auto;
        }
        .wave {
            width: 100%;
            height: 60px;
            margin: 0.5rem 0;
            border: 1px solid #0f0;
            background: #0a0a0a;
            position: relative;
            overflow: hidden;
        }
        .wave-label {
            position: absolute;
            left: 10px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 0.8rem;
            z-index: 10;
            font-weight: 600;
        }
        .wave-line {
            position: absolute;
            width: 100%;
            height: 100%;
            left: 0;
            top: 50%;
        }
        .back-link {
            display: inline-block;
            margin: 1rem;
            color: #0f0;
            text-decoration: none;
            border: 2px solid #0f0;
            padding: 0.5rem 1rem;
            font-weight: 600;
        }
        .back-link:hover {
            background: #0f0;
            color: #000;
        }
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-link">← HOME</a>
        <h1>MARKET EEG MONITOR</h1>
        <div class="eeg-container" id="eeg"></div>
    </div>
    
    <script>
        const domains = ['stock:AAPL', 'stock:MSFT', 'stock:GOOGL', 'stock:TSLA', 'stock:NVDA', 'crypto:BTC', 'crypto:ETH'];
        const eegContainer = document.getElementById('eeg');
        
        domains.forEach(domain => {
            const wave = document.createElement('div');
            wave.className = 'wave';
            wave.innerHTML = `<div class="wave-label">${domain}</div><svg class="wave-line" style="stroke: #0f0; fill: none; stroke-width: 2"></svg>`;
            eegContainer.appendChild(wave);
        });
        
        function generateWave(svg) {
            const width = svg.parentElement.offsetWidth;
            const height = svg.parentElement.offsetHeight;
            let points = [];
            for (let i = 0; i < width; i += 10) {
                const y = height / 2 + Math.sin(i / 30 + Date.now() / 500) * (height / 3);
                points.push([i, y]);
            }
            const pathData = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p[0]} ${p[1]}`).join(' ');
            svg.setAttribute('d', pathData);
        }
        
        document.querySelectorAll('.wave-line').forEach(svg => {
            setInterval(() => generateWave(svg), 50);
        });
    </script>
</body>
</html>
"""


class HTTPServer:
    """Async HTTP server for dashboards"""
    
    def __init__(self, port: int = 8080, metrics_callback=None):
        self.port = port
        self.metrics_callback = metrics_callback
        self.app = web.Application()
        self.setup_routes()
    
    def setup_routes(self):
        """Setup HTTP routes"""
        self.app.router.add_get('/', self.handle_index)
        self.app.router.add_get('/dashboard', self.handle_dashboard)
        self.app.router.add_get('/eeg', self.handle_eeg)
        self.app.router.add_get('/status', self.handle_status)
        self.app.router.add_get('/api/metrics', self.handle_metrics)
    
    async def handle_index(self, request):
        """Serve index page"""
        return web.Response(text=INDEX_HTML, content_type='text/html')
    
    async def handle_dashboard(self, request):
        """Serve consciousness dashboard"""
        return web.Response(text=DASHBOARD_HTML, content_type='text/html')
    
    async def handle_eeg(self, request):
        """Serve EEG monitor"""
        return web.Response(text=EEG_HTML, content_type='text/html')
    
    async def handle_status(self, request):
        """Serve status page"""
        status = {
            'status': 'online',
            'zeromq_network': 'active',
            'http_server': 'running',
            'port': self.port
        }
        return web.Response(text=f"<pre>{json.dumps(status, indent=2)}</pre>", content_type='text/html')
    
    async def handle_metrics(self, request):
        """Serve metrics as JSON"""
        if self.metrics_callback:
            metrics = self.metrics_callback()
            return web.json_response(metrics)
        return web.json_response({'status': 'metrics_unavailable'})
    
    async def start(self):
        """Start the HTTP server"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()
        logger.info(f"HTTP Server started on port {self.port}")
        return runner


async def start_http_server(port: int = 8080, metrics_callback=None):
    """Start HTTP server for dashboards"""
    server = HTTPServer(port=port, metrics_callback=metrics_callback)
    runner = await server.start()
    return runner
