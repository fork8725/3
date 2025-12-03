"""
Database architecture setup for Section 5.1:
- Relational (PostgreSQL via SQLAlchemy) — optional; current app uses SQLite for local dev
- Time-Series (InfluxDB)
- File Storage (MinIO)
- Graph Database (Neo4j)

This module provides lazy-initialized clients configured via environment variables.
No network calls are made on import; clients are created on demand.
"""
import os
from typing import Optional

# Relational: keep existing SQLite; optionally support PostgreSQL URL via env
DEFAULT_SQLALCHEMY_URL = os.getenv("SQLALCHEMY_DATABASE_URL", "sqlite:///./app.db")

# InfluxDB config
INFLUX_URL = os.getenv("INFLUX_URL", "http://localhost:8086")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "")
INFLUX_ORG = os.getenv("INFLUX_ORG", "")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "")

# MinIO config
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "")

# Neo4j config
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")

# Clients (lazy)
_influx_client = None
_minio_client = None
_neo4j_driver = None


def get_influx_client():
    """Return an InfluxDB client if credentials exist; otherwise None."""
    global _influx_client
    if _influx_client is not None:
        return _influx_client
    try:
        if INFLUX_TOKEN and INFLUX_URL:
            from influxdb_client import InfluxDBClient
            _influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
            return _influx_client
    except Exception:
        # Keep None if not available
        return None
    return None


def get_minio_client():
    """Return a MinIO client if credentials exist; otherwise None."""
    global _minio_client
    if _minio_client is not None:
        return _minio_client
    try:
        if MINIO_ACCESS_KEY and MINIO_SECRET_KEY and MINIO_ENDPOINT:
            from minio import Minio
            _minio_client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=MINIO_SECURE)
            return _minio_client
    except Exception:
        return None
    return None


def get_neo4j_driver():
    """Return a Neo4j driver if credentials exist; otherwise None."""
    global _neo4j_driver
    if _neo4j_driver is not None:
        return _neo4j_driver
    try:
        if NEO4J_URI and NEO4J_USER and NEO4J_PASSWORD:
            from neo4j import GraphDatabase
            _neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
            return _neo4j_driver
    except Exception:
        return None
    return None


# Example tiny helpers (no external calls unless clients configured):

def get_architecture_status() -> dict:
    """Return a status dictionary indicating which layers are configured."""
    return {
        "relational": True,  # SQLite (or PostgreSQL if env provided)
        "time_series_configured": bool(INFLUX_TOKEN and INFLUX_URL),
        "file_storage_configured": bool(MINIO_ACCESS_KEY and MINIO_SECRET_KEY and MINIO_ENDPOINT),
        "graph_configured": bool(NEO4J_URI and NEO4J_USER and NEO4J_PASSWORD),
    }

