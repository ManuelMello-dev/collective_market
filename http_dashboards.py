"""
HTTP Dashboards Server - Complete Cognitive Mesh Control Panel
Pure Python stdlib (no external dependencies)
"""
import threading
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import time

logger = logging.getLogger(__name__)

# Main Dashboard HTML
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cognitive Mesh Control Panel</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #000;
            color: #fff;
            line-height: 1.5;
        }
        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 2rem;
        }
        header {
            border-bottom: 4px solid #fff;
            padding-bottom: 1.5rem;
            margin-bottom: 2rem;
        }
        h1 {
            font-size: 3.5rem;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: -2px;
            margin-bottom: 0.5rem;
        }
        .subtitle {
            font-size: 1rem;
            opacity: 0.7;
            font-weight: 600;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        .panel {
            border: 3px solid #fff;
            padding: 1.5rem;
            background: #0a0a0a;
        }
        .panel h2 {
            font-size: 1.4rem;
            margin-bottom: 1rem;
            border-bottom: 2px solid #fff;
            padding-bottom: 0.5rem;
            text-transform: uppercase;
            font-weight: 700;
        }
        .stat-row {
            display: flex;
            justify-content: space-between;
            padding: 0.75rem 0;
            border-bottom: 1px solid #333;
            font-size: 0.95rem;
        }
        .stat-label {
            font-weight: 600;
            opacity: 0.8;
        }
        .stat-value {
            color: #0f0;
            font-family: 'Courier New', monospace;
            font-weight: 700;
        }
        .stat-row:last-child {
            border-bottom: none;
        }
        .full-width {
            grid-column: 1 / -1;
        }
        .concepts-list {
            max-height: 300px;
            overflow-y: auto;
            background: #111;
            padding: 1rem;
            border: 1px solid #333;
            margin-top: 1rem;
        }
        .concept-item {
            padding: 0.5rem;
            margin-bottom: 0.5rem;
            background: #1a1a1a;
            border-left: 3px solid #0f0;
            font-size: 0.85rem;
            font-family: 'Courier New', monospace;
            word-break: break-all;
        }
        .rules-list {
            max-height: 300px;
            overflow-y: auto;
            background: #111;
            padding: 1rem;
            border: 1px solid #333;
            margin-top: 1rem;
        }
        .rule-item {
            padding: 0.5rem;
            margin-bottom: 0.5rem;
            background: #1a1a1a;
            border-left: 3px solid #ff0;
            font-size: 0.85rem;
            font-family: 'Courier New', monospace;
            word-break: break-all;
        }
        .transfers-list {
            max-height: 300px;
            overflow-y: auto;
            background: #111;
            padding: 1rem;
            border: 1px solid #333;
            margin-top: 1rem;
        }
        .transfer-item {
            padding: 0.5rem;
            margin-bottom: 0.5rem;
            background: #1a1a1a;
            border-left: 3px solid #0ff;
            font-size: 0.85rem;
            font-family: 'Courier New', monospace;
        }
        .goals-list {
            max-height: 300px;
            overflow-y: auto;
            background: #111;
            padding: 1rem;
            border: 1px solid #333;
            margin-top: 1rem;
        }
        .goal-item {
            padding: 0.5rem;
            margin-bottom: 0.5rem;
            background: #1a1a1a;
            border-left: 3px solid #f0f;
            font-size: 0.85rem;
            font-family: 'Courier New', monospace;
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #0f0;
            margin-right: 0.5rem;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .error-indicator {
            background: #f00;
        }
        .chart-container {
            background: #111;
            padding: 1rem;
            border: 1px solid #333;
            margin-top: 1rem;
            min-height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.9rem;
            color: #666;
        }
        .refresh-time {
            font-size: 0.75rem;
            opacity: 0.5;
            margin-top: 1rem;
            text-align: right;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>COGNITIVE MESH</h1>
            <div class="subtitle">
                <span class="status-indicator"></span>
                Real-time Market Intelligence System
            </div>
        </header>
        
        <div class="grid">
            <!-- System Status -->
            <div class="panel">
                <h2>SYSTEM STATUS</h2>
                <div class="stat-row">
                    <span class="stat-label">Status</span>
                    <span class="stat-value" id="status">ONLINE</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Uptime</span>
                    <span class="stat-value" id="uptime">0s</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Errors</span>
                    <span class="stat-value" id="errors">0</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Last Update</span>
                    <span class="stat-value" id="last-update">--:--:--</span>
                </div>
            </div>
            
            <!-- Cognitive Metrics -->
            <div class="panel">
                <h2>COGNITIVE STATE</h2>
                <div class="stat-row">
                    <span class="stat-label">Concepts Formed</span>
                    <span class="stat-value" id="concepts">0</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Rules Learned</span>
                    <span class="stat-value" id="rules">0</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Transfers Made</span>
                    <span class="stat-value" id="transfers">0</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Goals Generated</span>
                    <span class="stat-value" id="goals">0</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Observations</span>
                    <span class="stat-value" id="observations">0</span>
                </div>
            </div>
            
            <!-- Market Coverage -->
            <div class="panel">
                <h2>MARKET COVERAGE</h2>
                <div class="stat-row">
                    <span class="stat-label">Symbols Tracked</span>
                    <span class="stat-value">7</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Stocks</span>
                    <span class="stat-value">5</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Crypto</span>
                    <span class="stat-value">2</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Active Domains</span>
                    <span class="stat-value" id="domains">0</span>
                </div>
            </div>
            
            <!-- Concepts Panel -->
            <div class="panel full-width">
                <h2>CONCEPTS FORMED</h2>
                <div class="concepts-list" id="concepts-list">
                    <div class="concept-item">Waiting for concepts...</div>
                </div>
            </div>
            
            <!-- Rules Panel -->
            <div class="panel full-width">
                <h2>RULES LEARNED</h2>
                <div class="rules-list" id="rules-list">
                    <div class="rule-item">Waiting for rules...</div>
                </div>
            </div>
            
            <!-- Transfers Panel -->
            <div class="panel full-width">
                <h2>CROSS-DOMAIN TRANSFERS</h2>
                <div class="transfers-list" id="transfers-list">
                    <div class="transfer-item">Waiting for transfers...</div>
                </div>
            </div>
            
            <!-- Goals Panel -->
            <div class="panel full-width">
                <h2>AUTONOMOUS GOALS</h2>
                <div class="goals-list" id="goals-list">
                    <div class="goal-item">Waiting for goals...</div>
                </div>
            </div>
        </div>
        
        <div class="refresh-time">
            Last updated: <span id="refresh-time">--:--:--</span> | Auto-refresh every 2 seconds
        </div>
    </div>
    
    <script>
        async function updateDashboard() {
            try {
                const response = await fetch('/api/metrics');
                const data = await response.json();
                
                // Update basic metrics
                document.getElementById('uptime').textContent = formatUptime(data.uptime_seconds || 0);
                document.getElementById('concepts').textContent = data.concepts_formed || 0;
                document.getElementById('rules').textContent = data.rules_learned || 0;
                document.getElementById('transfers').textContent = data.transfers_made || 0;
                document.getElementById('goals').textContent = data.goals_generated || 0;
                document.getElementById('observations').textContent = data.total_observations || 0;
                document.getElementById('errors').textContent = data.errors || 0;
                document.getElementById('domains').textContent = data.domains_tracked || 0;
                
                // Update concepts list
                if (data.concepts && data.concepts.length > 0) {
                    const conceptsList = document.getElementById('concepts-list');
                    conceptsList.innerHTML = data.concepts.map(c => 
                        `<div class="concept-item">${c.domain}: ${c.id.substring(0, 16)}... (confidence: ${(c.confidence * 100).toFixed(0)}%)</div>`
                    ).join('');
                }
                
                // Update rules list
                if (data.rules && data.rules.length > 0) {
                    const rulesList = document.getElementById('rules-list');
                    rulesList.innerHTML = data.rules.map(r => 
                        `<div class="rule-item">${r.condition} → ${r.consequence}</div>`
                    ).join('');
                }
                
                // Update transfers list
                if (data.transfers && data.transfers.length > 0) {
                    const transfersList = document.getElementById('transfers-list');
                    transfersList.innerHTML = data.transfers.map(t => 
                        `<div class="transfer-item">${t.source} → ${t.target}</div>`
                    ).join('');
                }
                
                // Update goals list
                if (data.goals && data.goals.length > 0) {
                    const goalsList = document.getElementById('goals-list');
                    goalsList.innerHTML = data.goals.map(g => 
                        `<div class="goal-item">${g}</div>`
                    ).join('');
                }
                
                // Update timestamp
                const now = new Date();
                document.getElementById('refresh-time').textContent = now.toLocaleTimeString();
                document.getElementById('last-update').textContent = now.toLocaleTimeString();
                
            } catch (e) {
                console.error('Error fetching metrics:', e);
                document.getElementById('status').textContent = 'ERROR';
                document.getElementById('status').parentElement.querySelector('.stat-value').style.color = '#f00';
            }
        }
        
        function formatUptime(seconds) {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            const secs = Math.floor(seconds % 60);
            return `${hours}h ${minutes}m ${secs}s`;
        }
        
        // Initial update
        updateDashboard();
        
        // Auto-refresh every 2 seconds
        setInterval(updateDashboard, 2000);
    </script>
</body>
</html>
"""

class DashboardHandler(BaseHTTPRequestHandler):
    """HTTP request handler for dashboards"""
    
    metrics_callback = None
    startup_logged = False
    
    def do_GET(self):
        """Handle GET requests"""
        if not DashboardHandler.startup_logged:
            logger.info("HTTP Dashboards Server is ONLINE")
            DashboardHandler.startup_logged = True
        
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/' or path == '/dashboard':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode('utf-8'))
        
        elif path == '/api/metrics':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            metrics = {
                'concepts_formed': 0,
                'rules_learned': 0,
                'transfers_made': 0,
                'goals_generated': 0,
                'total_observations': 0,
                'uptime_seconds': 0,
                'errors': 0,
                'domains_tracked': 0,
                'concepts': [],
                'rules': [],
                'transfers': [],
                'goals': []
            }
            
            if self.metrics_callback:
                try:
                    metrics = self.metrics_callback()
                except Exception as e:
                    logger.debug(f"Metrics callback error: {e}")
            
            self.wfile.write(json.dumps(metrics).encode())
        
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<h1>404 Not Found</h1>")
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        logger.debug(format % args)


def start_http_dashboards(port: int = 8080, metrics_callback=None):
    """Start HTTP dashboards server in a background thread"""
    DashboardHandler.metrics_callback = metrics_callback
    
    server = HTTPServer(('0.0.0.0', port), DashboardHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    
    logger.info(f"✓ HTTP Dashboards started on port {port}")
    logger.info(f"  - Dashboard: http://0.0.0.0:{port}/")
    logger.info(f"  - Metrics API: http://0.0.0.0:{port}/api/metrics")
    
    return server
