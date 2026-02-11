/**
 * Integration helpers for collective_market microservices
 * Connects to Redis (episodic), MySQL (long-term), InfluxDB (metrics), and ZMQ (message bus)
 */

import * as redis from "redis";
import mysql from "mysql2/promise";
import * as zmq from "zeromq";

// Redis Connection (Episodic Memory)
let redisClient: redis.RedisClientType | null = null;

export async function getRedisClient() {
  if (redisClient) return redisClient;

  try {
    const host = process.env.REDIS_HOST || "localhost";
    const port = parseInt(process.env.REDIS_PORT || "6379");

    redisClient = redis.createClient({
      socket: {
        host,
        port,
        reconnectStrategy: (retries: number) => Math.min(retries * 50, 500),
      },
    });

    redisClient.on("error", (err: unknown) => console.error("Redis error:", err));
    await redisClient.connect();

    console.log(`[Redis] Connected to ${host}:${port}`);
    return redisClient;
  } catch (error) {
    console.error("[Redis] Connection failed:", error);
    return null;
  }
}

export async function getRedisData(key: string): Promise<unknown | null> {
  try {
    const client = await getRedisClient();
    if (!client) return null;

    const value = await client.get(key);
    return value ? JSON.parse(value) : null;
  } catch (error) {
    console.error(`[Redis] Failed to get ${key}:`, error);
    return null;
  }
}

export async function setRedisData(
  key: string,
  value: unknown,
  ttl?: number
): Promise<boolean> {
  try {
    const client = await getRedisClient();
    if (!client) return false;

    if (ttl) {
      await client.setEx(key, ttl, JSON.stringify(value));
    } else {
      await client.set(key, JSON.stringify(value));
    }
    return true;
  } catch (error) {
    console.error(`[Redis] Failed to set ${key}:`, error);
    return false;
  }
}

// InfluxDB Connection (Time-Series Metrics)
let influxClient: unknown | null = null;

export async function getInfluxDBClient() {
  // InfluxDB client initialization would go here
  // For now, returning null as placeholder for integration
  return null;
}

export async function queryInfluxDB(
  bucket: string,
  query: string
): Promise<unknown[] | null> {
  try {
    // Query implementation would connect to InfluxDB
    // Placeholder for now
    console.log(`[InfluxDB] Would query bucket ${bucket}`);
    return [];
  } catch (error) {
    console.error("[InfluxDB] Query failed:", error);
    return null;
  }
}

// ZMQ Connection (Message Bus)
let zmqSocket: zmq.Subscriber | null = null;

export async function getZMQSubscriber(
  host: string = "localhost",
  port: number = 5555
) {
  if (zmqSocket) return zmqSocket;

  try {
    zmqSocket = new zmq.Subscriber();
    const endpoint = `tcp://${host}:${port}`;

    zmqSocket.connect(endpoint);
    console.log(`[ZMQ] Subscribed to ${endpoint}`);

    return zmqSocket;
  } catch (error) {
    console.error("[ZMQ] Connection failed:", error);
    return null;
  }
}

export async function subscribeToZMQTopic(
  topic: string,
  callback: (message: unknown) => void
) {
  try {
    const socket = await getZMQSubscriber();
    if (!socket) return;

    socket.subscribe(topic);
    console.log(`[ZMQ] Subscribed to topic: ${topic}`);

    // Listen for messages
    for await (const [msg] of socket) {
      try {
        const data = JSON.parse(msg.toString());
        callback(data);
      } catch (e) {
        console.error("[ZMQ] Failed to parse message:", e);
      }
    }
  } catch (error) {
    console.error(`[ZMQ] Subscription failed:`, error);
  }
}

// MySQL Connection (Long-Term Memory - for collective_market data)
let mysqlPool: mysql.Pool | null = null;

export async function getMySQLPool() {
  if (mysqlPool) return mysqlPool;

  try {
    const host = process.env.MYSQL_HOST || "localhost";
    const user = process.env.MYSQL_USER || "market";
    const password = process.env.MYSQL_PASSWORD || "market_pass";
    const database = process.env.MYSQL_DB || "market_memory";

    mysqlPool = mysql.createPool({
      host,
      user,
      password,
      database,
      waitForConnections: true,
      connectionLimit: 10,
      queueLimit: 0,
    });

    console.log(`[MySQL] Connected to ${host}/${database}`);
    return mysqlPool;
  } catch (error) {
    console.error("[MySQL] Connection failed:", error);
    return null;
  }
}

export async function queryMySQL(
  sql: string,
  params: unknown[] = []
): Promise<unknown[] | null> {
  try {
    const pool = await getMySQLPool();
    if (!pool) return null;

    const connection = await pool.getConnection();
    const [rows] = await connection.execute(sql, params);
    connection.release();

    return rows as unknown[];
  } catch (error) {
    console.error("[MySQL] Query failed:", error);
    return null;
  }
}

// Health Check Functions
export async function checkRedisHealth(): Promise<boolean> {
  try {
    const client = await getRedisClient();
    if (!client) return false;

    await client.ping();
    return true;
  } catch {
    return false;
  }
}

export async function checkInfluxDBHealth(): Promise<boolean> {
  try {
    const client = await getInfluxDBClient();
    if (!client) return false;

    // InfluxDB health check would go here
    return true;
  } catch {
    return false;
  }
}

export async function checkMySQLHealth(): Promise<boolean> {
  try {
    const pool = await getMySQLPool();
    if (!pool) return false;

    const connection = await pool.getConnection();
    await connection.ping();
    connection.release();

    return true;
  } catch {
    return false;
  }
}

export async function checkZMQHealth(): Promise<boolean> {
  try {
    const socket = await getZMQSubscriber();
    return socket !== null;
  } catch {
    return false;
  }
}

// System Health Overview
export async function getSystemHealth() {
  return {
    redis: await checkRedisHealth(),
    influxdb: await checkInfluxDBHealth(),
    mysql: await checkMySQLHealth(),
    zmq: await checkZMQHealth(),
    timestamp: new Date().toISOString(),
  };
}
