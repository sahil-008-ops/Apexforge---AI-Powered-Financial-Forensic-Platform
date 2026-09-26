"""
ApexForge Configuration Settings
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SYNTHETIC_DOCS_DIR = DATA_DIR / "synthetic_docs"
CHROMA_DB_DIR = DATA_DIR / "chroma_db"

# Ensure required directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
SYNTHETIC_DOCS_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)

# Graph Engine Settings
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
USE_NEO4J = os.getenv("USE_NEO4J", "False").lower() in ("true", "1", "yes")

# Anomaly Detection Settings
STRUCTURING_THRESHOLD = 10000.0  # CTR Reporting threshold
RAPID_MOVEMENT_WINDOW_HOURS = 48
HIGH_AMOUNT_PERCENTILE = 95.0
ISOLATION_FOREST_CONTAMINATION = 0.15

# Audit Ledger Settings
LEDGER_FILE = DATA_DIR / "forensic_ledger.json"
