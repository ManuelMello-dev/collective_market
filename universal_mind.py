#!/usr/bin/env python3
"""
Universal Cognitive Core v0.3 - Integrated into collective_market
Pattern-hungry mind with Redis episodic memory, MySQL persistence, InfluxDB metrics, and ZMQ publishing.
"""

import asyncio
import random
import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import zmq
import zmq.asyncio

import redis
import yfinance as yf
from polygon import RESTClient

# Database imports
import mysql.connector
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("UniversalMind")


@dataclass
class Concept:
    id: str
    examples: List[Dict]
    confidence: float = 0.0
    domain: str = "unknown"


@dataclass
class Rule:
    antecedent: str
    consequent: str
    confidence: float = 0.6


class UniversalCognitiveCore:
    """
    Pure pattern-learning system that forms concepts, infers rules, and transfers knowledge
    across domains. Integrates with Redis (episodic), MySQL (persistence), InfluxDB (metrics),
    and ZMQ (publishing).
    """

    def __init__(self, mind_id: str = "wanderer-001"):
        self.mind_id = mind_id
        self.iteration = 0
        self.running = False

        self.concepts: Dict[str, Concept] = {}
        self.rules: List[Rule] = []
        self.short_term_memory: List[Dict] = []
        self.cross_domain_mappings: Dict = {}

        self.metrics = {
            "concepts_formed": 0,
            "rules_learned": 0,
            "transfers_made": 0,
            "goals_generated": 0,
            "total_observations": 0
        }

        # Initialize external connections
        self._init_redis()
        self._init_mysql()
        self._init_influxdb()
        self._init_zmq()

        logger.info(f"🌌 Universal Mind {mind_id} awakened — integrated with collective_market")

    def _init_redis(self):
        """Initialize Redis connection for episodic memory"""
        try:
            self.redis_client = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                decode_responses=True
            )
            self.redis_client.ping()
            logger.info("✓ Redis episodic memory connected")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            self.redis_client = None

    def _init_mysql(self):
        """Initialize MySQL connection for long-term persistence"""
        try:
            self.mysql_conn = mysql.connector.connect(
                host=os.getenv("MYSQL_HOST", "localhost"),
                user=os.getenv("MYSQL_USER", "root"),
                password=os.getenv("MYSQL_PASSWORD", ""),
                database=os.getenv("MYSQL_DB", "collective_market")
            )
            self.mysql_cursor = self.mysql_conn.cursor()
            self._create_mysql_tables()
            logger.info("✓ MySQL long-term memory connected")
        except Exception as e:
            logger.warning(f"MySQL connection failed: {e}")
            self.mysql_conn = None

    def _create_mysql_tables(self):
        """Create tables for concepts and rules if they don't exist"""
        if not self.mysql_conn:
            return

        try:
            self.mysql_cursor.execute("""
                CREATE TABLE IF NOT EXISTS concepts (
                    id VARCHAR(255) PRIMARY KEY,
                    domain VARCHAR(100),
                    confidence FLOAT,
                    examples JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)

            self.mysql_cursor.execute("""
                CREATE TABLE IF NOT EXISTS rules (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    antecedent VARCHAR(255),
                    consequent VARCHAR(255),
                    confidence FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.mysql_cursor.execute("""
                CREATE TABLE IF NOT EXISTS cognitive_state (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    mind_id VARCHAR(255),
                    iteration INT,
                    concepts_count INT,
                    rules_count INT,
                    domains_count INT,
                    transfers_count INT,
                    goals_count INT,
                    memory_size INT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.mysql_conn.commit()
            logger.info("✓ MySQL tables initialized")
        except Exception as e:
            logger.error(f"Failed to create MySQL tables: {e}")

    def _init_influxdb(self):
        """Initialize InfluxDB connection for metrics"""
        try:
            self.influx_client = InfluxDBClient(
                url=os.getenv("INFLUXDB_URL", "http://localhost:8086"),
                token=os.getenv("INFLUXDB_TOKEN", ""),
                org=os.getenv("INFLUXDB_ORG", "collective_market")
            )
            self.influx_write_api = self.influx_client.write_api(write_type=SYNCHRONOUS)
            logger.info("✓ InfluxDB metrics connected")
        except Exception as e:
            logger.warning(f"InfluxDB connection failed: {e}")
            self.influx_client = None

    def _init_zmq(self):
        """Initialize ZMQ context for publishing insights"""
        try:
            self.zmq_context = zmq.asyncio.Context()
            self.zmq_socket = self.zmq_context.socket(zmq.PUB)
            zmq_endpoint = os.getenv("ZMQ_ENDPOINT", "tcp://127.0.0.1:5555")
            self.zmq_socket.bind(zmq_endpoint)
            logger.info(f"✓ ZMQ publisher bound to {zmq_endpoint}")
        except Exception as e:
            logger.warning(f"ZMQ initialization failed: {e}")
            self.zmq_socket = None

    def ingest(self, observation: Dict[str, Any], domain: str = "raw") -> Dict:
        """Ingest observation and form concepts/rules"""
        self.iteration += 1
        self.metrics["total_observations"] += 1

        # Store in short-term memory
        self.short_term_memory.append(observation)
        if len(self.short_term_memory) > 300:
            self.short_term_memory.pop(0)

        # Store in Redis episodic memory
        if self.redis_client:
            try:
                key = f"observation:{self.iteration}"
                self.redis_client.setex(key, 3600, json.dumps(observation))  # 1 hour TTL
            except Exception as e:
                logger.debug(f"Redis store failed: {e}")

        # Form concepts and infer rules
        concept_id = self._form_concept(observation, domain)
        new_rules = self._infer_rules(observation)
        for rule in new_rules:
            self.rules.append(rule)
            self.metrics["rules_learned"] += 1

        # Cross-domain transfer
        if len({c.domain for c in self.concepts.values()}) > 1:
            self._attempt_cross_domain_transfer(domain)

        # Generate autonomous goals
        if self.iteration % 12 == 0:
            self._generate_autonomous_goals(observation)

        result = {
            "iteration": self.iteration,
            "concept_formed": concept_id,
            "new_rules": len(new_rules),
            "current_concepts": len(self.concepts),
            "symbol": observation.get("symbol", "unknown")
        }

        return result

    def _form_concept(self, obs: Dict, domain: str) -> str:
        """Form concepts based on signature-based matching"""
        signature = frozenset(
            (k, round(v, 3) if isinstance(v, float) else v)
            for k, v in obs.items() if not k.startswith("_") and v is not None
        )
        concept_id = f"concept_{hash(signature) % 999999}"

        if concept_id not in self.concepts:
            self.concepts[concept_id] = Concept(
                id=concept_id,
                examples=[obs],
                confidence=0.3,
                domain=domain
            )
            self.metrics["concepts_formed"] += 1
            logger.info(f"🧩 New concept born: {concept_id} in {domain} | {obs.get('symbol')}")

            # Persist to MySQL
            if self.mysql_conn:
                try:
                    self.mysql_cursor.execute(
                        "INSERT INTO concepts (id, domain, confidence, examples) VALUES (%s, %s, %s, %s)",
                        (concept_id, domain, 0.3, json.dumps([obs]))
                    )
                    self.mysql_conn.commit()
                except Exception as e:
                    logger.debug(f"MySQL insert failed: {e}")

            return concept_id

        self.concepts[concept_id].examples.append(obs)
        self.concepts[concept_id].confidence = min(1.0, self.concepts[concept_id].confidence + 0.18)
        return concept_id

    def _infer_rules(self, obs: Dict) -> List[Rule]:
        """Infer rules from multi-dimensional relationships"""
        rules = []
        keys = [k for k in obs.keys() if isinstance(obs[k], (int, float))]

        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                k1, k2 = keys[i], keys[j]
                v1, v2 = obs[k1], obs[k2]
                if v1 > 0.75 * v2:
                    rules.append(Rule(f"{k1}_strong", f"{k2}_elevated", 0.75))

        return rules[:4]

    def _attempt_cross_domain_transfer(self, current_domain: str):
        """Attempt to transfer patterns across domains"""
        for other in {c.domain for c in self.concepts.values()}:
            if other != current_domain:
                key = f"{current_domain}→{other}"
                if key not in self.cross_domain_mappings:
                    self.cross_domain_mappings[key] = True
                    self.metrics["transfers_made"] += 1
                    logger.info(f"🔄 Cross-domain transfer: {current_domain} → {other}")

    def _generate_autonomous_goals(self, obs: Dict):
        """Generate autonomous research goals"""
        goal = {
            "id": f"goal_{self.metrics['goals_generated']+1}",
            "description": f"Decode why {list(obs.keys())[:4]} move together in {obs.get('symbol', 'market')}",
            "priority": random.uniform(0.65, 0.97)
        }
        self.metrics["goals_generated"] += 1
        logger.info(f"🌱 New goal spawned: {goal['description']}")

    def introspect(self) -> Dict:
        """Return current cognitive state"""
        state = {
            "mind_id": self.mind_id,
            "age": self.iteration,
            "concepts": len(self.concepts),
            "rules": len(self.rules),
            "domains": len({c.domain for c in self.concepts.values()}),
            "transfers": self.metrics["transfers_made"],
            "goals": self.metrics["goals_generated"],
            "memory": len(self.short_term_memory),
            "status": "wandering" if self.iteration > 30 else "awakening"
        }

        # Persist to MySQL
        if self.mysql_conn:
            try:
                self.mysql_cursor.execute(
                    """INSERT INTO cognitive_state 
                       (mind_id, iteration, concepts_count, rules_count, domains_count, transfers_count, goals_count, memory_size)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                    (self.mind_id, self.iteration, state["concepts"], state["rules"],
                     state["domains"], state["transfers"], state["goals"], state["memory"])
                )
                self.mysql_conn.commit()
            except Exception as e:
                logger.debug(f"MySQL insert failed: {e}")

        # Publish to InfluxDB
        if self.influx_client:
            try:
                from influxdb_client.client.write_api import Point
                point = Point("cognitive_state") \
                    .tag("mind_id", self.mind_id) \
                    .field("concepts", state["concepts"]) \
                    .field("rules", state["rules"]) \
                    .field("domains", state["domains"]) \
                    .field("transfers", state["transfers"]) \
                    .field("goals", state["goals"]) \
                    .field("memory", state["memory"])
                self.influx_write_api.write(bucket="collective_market", record=point)
            except Exception as e:
                logger.debug(f"InfluxDB write failed: {e}")

        return state

    async def publish_insight(self, insight: Dict):
        """Publish insight via ZMQ"""
        if self.zmq_socket:
            try:
                message = json.dumps(insight).encode('utf-8')
                await self.zmq_socket.send(b"cognitive_insight " + message)
                logger.debug(f"Published insight: {insight.get('type', 'unknown')}")
            except Exception as e:
                logger.debug(f"ZMQ publish failed: {e}")

    def shutdown(self):
        """Gracefully shutdown all connections"""
        if self.redis_client:
            self.redis_client.close()
        if self.mysql_conn:
            self.mysql_cursor.close()
            self.mysql_conn.close()
        if self.influx_client:
            self.influx_client.close()
        if self.zmq_socket:
            self.zmq_socket.close()
        logger.info(f"🌌 Universal Mind {self.mind_id} entering dormancy")


# ============= MARKET WANDERER =============

MARKET_SYMBOLS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "AMD",
    "SMCI", "AVGO", "ORCL", "CRM", "ADBE", "NFLX", "INTC", "ARM",
    "BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD"
]


def fetch_yfinance(symbol: str) -> Dict:
    """Fetch data from yfinance"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="2d", interval="1m")
        if not hist.empty:
            latest = hist.iloc[-1]
            return {
                "datetime": latest.name.strftime("%Y-%m-%d %H:%M:%S"),
                "open": float(latest["Open"]),
                "high": float(latest["High"]),
                "low": float(latest["Low"]),
                "close": float(latest["Close"]),
                "volume": int(latest["Volume"]),
                "symbol": symbol
            }
        return {"error": "no_data"}
    except Exception as e:
        logger.debug(f"yfinance failed {symbol}: {e}")
        return {"error": "yf_error"}


def fetch_polygon(symbol: str, client: RESTClient) -> Dict:
    """Fetch data from Polygon API"""
    try:
        to_date = datetime.now()
        from_date = to_date - timedelta(days=3)

        aggs = client.get_aggs(
            ticker=symbol,
            multiplier=1,
            timespan="minute",
            from_=from_date.strftime("%Y-%m-%d"),
            to=to_date.strftime("%Y-%m-%d"),
            limit=10
        )

        if aggs:
            latest = aggs[-1]
            return {
                "datetime": datetime.fromtimestamp(latest.timestamp / 1000).strftime("%Y-%m-%d %H:%M:%S"),
                "open": latest.open,
                "high": latest.high,
                "low": latest.low,
                "close": latest.close,
                "volume": latest.volume,
                "symbol": symbol
            }
        return {"error": "no_data"}
    except Exception as e:
        logger.debug(f"Polygon failed {symbol}: {e}")
        return {"error": "poly_error"}


async def fetch_market_data(symbol: str, polygon_client: Optional[RESTClient] = None) -> Dict:
    """Fetch market data with fallback"""
    data = await asyncio.to_thread(fetch_yfinance, symbol)
    if not data.get("error"):
        return data

    if polygon_client:
        data = await asyncio.to_thread(fetch_polygon, symbol, polygon_client)
        if not data.get("error"):
            return data

    return {"error": "fetch_failed"}


def transform_market_data(raw: Dict) -> Dict:
    """Transform raw market data for cognitive ingestion"""
    transformed = {"domain": "finance"}

    for k in ["open", "high", "low", "close", "volume"]:
        if k in raw:
            transformed[k] = raw[k]

    if "close" in transformed and "open" in transformed:
        transformed["price_change"] = transformed["close"] - transformed["open"]

    if "datetime" in raw:
        transformed["timestamp"] = raw["datetime"]
    if "symbol" in raw:
        transformed["symbol"] = raw["symbol"]

    return {k: v for k, v in transformed.items() if v is not None}


async def wander_the_market(
    symbols: List[str],
    polygon_key: str,
    mind: UniversalCognitiveCore,
    delay_seconds: int = 18,
    max_iterations: int = 2000
):
    """Main market wandering loop"""
    logger.info(f"🌍 Mind is now wandering {len(symbols)} assets...")

    polygon_client = RESTClient(polygon_key) if polygon_key and polygon_key != "YOUR_KEY" else None

    for i in range(max_iterations):
        symbol = random.choice(symbols)
        logger.info(f"[{i+1:04d}] Wandering → {symbol}")

        raw = await fetch_market_data(symbol, polygon_client)

        if not raw.get("error"):
            obs = transform_market_data(raw)
            result = mind.ingest(obs, domain="finance")

            # Publish insight
            await mind.publish_insight({
                "type": "observation_ingested",
                "iteration": result["iteration"],
                "symbol": symbol,
                "concept": result["concept_formed"]
            })

            if (i + 1) % 5 == 0:
                state = mind.introspect()
                logger.info(f"🧠 Introspection: {state}")
        else:
            logger.warning(f"Failed to fetch {symbol}")

        await asyncio.sleep(delay_seconds)


async def main():
    """Main entry point"""
    POLYGON_API_KEY = os.getenv("POLYGON_API_KEY", "YOUR_KEY")

    mind = UniversalCognitiveCore("market_wanderer")

    try:
        await wander_the_market(
            MARKET_SYMBOLS,
            POLYGON_API_KEY,
            mind,
            delay_seconds=18,
            max_iterations=2000
        )
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    finally:
        mind.shutdown()

    logger.info("\n" + "="*70)
    logger.info("FINAL MIND STATE AFTER WANDERING")
    logger.info("="*70)
    print(json.dumps(mind.introspect(), indent=2))


if __name__ == "__main__":
    asyncio.run(main())
