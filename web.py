"""
FastAPI Web Service for Market Intelligence System
Provides health checks, status endpoints, and Prometheus metrics integration
"""
import os
import sys
import time
from datetime import datetime
from typing import Dict, Optional
import logging

from fastapi import FastAPI, Response
from fastapi.responses import PlainTextResponse
import uvicorn

# Try to import prometheus_client for metrics endpoint
try:
    from prometheus_client import REGISTRY, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Market Intelligence System",
    description="Production market intelligence and portfolio management system",
    version="1.0.0"
)

# Store startup time
STARTUP_TIME = datetime.now()


@app.get("/")
async def root():
    """Root endpoint with basic system info"""
    return {
        "service": "Market Intelligence System",
        "version": "1.0.0",
        "status": "running",
        "uptime_seconds": (datetime.now() - STARTUP_TIME).total_seconds()
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for Railway and load balancers
    Returns basic system health status
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": (datetime.now() - STARTUP_TIME).total_seconds(),
        "service": "web"
    }


@app.get("/status")
async def status():
    """
    Detailed status endpoint with runtime information
    Returns system configuration and environment details
    """
    # Check for environment variable presence
    env_vars = {
        "REDIS_URL": os.getenv("REDIS_URL") is not None,
        "REDIS_HOST": os.getenv("REDIS_HOST") is not None,
        "MYSQL_HOST": os.getenv("MYSQL_HOST") is not None,
        "MYSQL_USER": os.getenv("MYSQL_USER") is not None,
        "MYSQL_PASSWORD": os.getenv("MYSQL_PASSWORD") is not None,
        "MYSQL_DATABASE": os.getenv("MYSQL_DATABASE") is not None,
        "INFLUXDB_URL": os.getenv("INFLUXDB_URL") is not None,
        "INFLUXDB_TOKEN": os.getenv("INFLUXDB_TOKEN") is not None,
        "POLYGON_API_KEY": os.getenv("POLYGON_API_KEY") is not None,
        "ALPACA_KEY": os.getenv("ALPACA_KEY") is not None,
    }
    
    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": (datetime.now() - STARTUP_TIME).total_seconds(),
        "python_version": sys.version,
        "environment_variables_configured": env_vars,
        "prometheus_available": PROMETHEUS_AVAILABLE,
        "service_type": "web"
    }


@app.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint
    
    If prometheus_client is available and metrics are being collected by the worker,
    this endpoint exposes them in Prometheus format.
    
    Note: For full metrics, the worker service must be running with metrics enabled.
    This web service can share the same metrics registry if running in the same process,
    or you should configure Prometheus to scrape the worker's metrics port directly.
    """
    if not PROMETHEUS_AVAILABLE:
        return PlainTextResponse(
            content="# Prometheus client not available\n"
                    "# Install prometheus-client to enable metrics\n"
                    "# TODO: Install prometheus-client package\n",
            media_type="text/plain"
        )
    
    try:
        # Generate Prometheus metrics
        metrics_output = generate_latest(REGISTRY)
        return Response(content=metrics_output, media_type="text/plain")
    except Exception as e:
        logger.error(f"Error generating metrics: {e}")
        return PlainTextResponse(
            content=f"# Error generating metrics: {str(e)}\n"
                    f"# Note: Worker service should expose metrics on its own port\n"
                    f"# This web endpoint is for basic health checks\n",
            media_type="text/plain"
        )


@app.get("/ready")
async def readiness_check():
    """
    Readiness check for Kubernetes/Railway
    Indicates whether the service is ready to accept traffic
    """
    return {
        "ready": True,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/live")
async def liveness_check():
    """
    Liveness check for Kubernetes/Railway
    Indicates whether the service is alive and should not be restarted
    """
    return {
        "alive": True,
        "timestamp": datetime.now().isoformat()
    }


def main():
    """
    Main entry point for running the web service
    
    In production (Railway), the PORT environment variable is set automatically.
    Locally, defaults to 8000.
    """
    # Get port from environment or use default
    port = int(os.getenv("PORT", "8000"))
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info(f"Starting web service on port {port}")
    logger.info(f"Health check available at: http://0.0.0.0:{port}/health")
    logger.info(f"Status endpoint available at: http://0.0.0.0:{port}/status")
    logger.info(f"Metrics endpoint available at: http://0.0.0.0:{port}/metrics")
    
    # Run uvicorn server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )


if __name__ == "__main__":
    main()
