"""
Agent 3 — Anomaly Agent
Runs 12-category forensic rule evaluation, statistical Isolation Forest, and graph cycle detection.
"""

from typing import List, Tuple
from apexforge.models.data_models import (
    Transaction,
    Entity,
    Relationship,
    TransactionCycle,
    NormalizedDocument,
    AnomalyFinding,
)
from apexforge.graph.graph_store import TransactionGraphStore
from apexforge.graph.cycle_detector import CycleDetector
from apexforge.anomaly.anomaly_engine import AnomalyEngine


class AnomalyAgent:
    def __init__(self, graph_store: TransactionGraphStore):
        self.graph_store = graph_store
        self.cycle_detector = CycleDetector(graph_store)
        self.anomaly_engine = AnomalyEngine()

    def analyze_anomalies(
        self,
        transactions: List[Transaction],
        entities: List[Entity],
        relationships: List[Relationship],
        documents: List[NormalizedDocument],
    ) -> Tuple[List[TransactionCycle], List[AnomalyFinding]]:
        # 1. Circular Transaction Graph Detection
        cycles = self.cycle_detector.detect_circular_transactions()

        # 2. Anomaly Evaluation across 12 categories
        anomalies = self.anomaly_engine.evaluate_anomalies(
            transactions=transactions,
            entities=entities,
            relationships=relationships,
            cycles=cycles,
            documents=documents,
        )

        return cycles, anomalies
