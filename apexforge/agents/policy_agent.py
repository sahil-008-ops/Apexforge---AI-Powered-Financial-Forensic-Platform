"""
Agent 4 — Policy / Verification Agent
Uses RAG over indexed ChromaDB vector store to match detected anomalies against internal financial policies.
"""

from typing import List
from apexforge.models.data_models import AnomalyFinding, PolicyFinding
from apexforge.rag.policy_store import RAGPolicyStore


class PolicyAgent:
    def __init__(self, policy_store: RAGPolicyStore):
        self.policy_store = policy_store

    def verify_anomalies_against_policies(
        self, anomalies: List[AnomalyFinding]
    ) -> List[PolicyFinding]:
        all_policy_findings: List[PolicyFinding] = []

        for anomaly in anomalies:
            findings = self.policy_store.verify_finding_against_policies(
                anomaly_type=anomaly.anomaly_type.value,
                explanation=anomaly.explanation,
            )
            all_policy_findings.extend(findings)

        return all_policy_findings
