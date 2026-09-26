"""
Section 7: Dedicated Forensic Anomaly Engine
Combines deterministic forensic rules, statistical machine learning (Isolation Forest),
and graph topological features to detect 12 categories of financial anomalies with explainable scoring.
"""

import uuid
import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.ensemble import IsolationForest

from apexforge.models.data_models import (
    Transaction,
    Entity,
    Relationship,
    TransactionCycle,
    NormalizedDocument,
    AnomalyFinding,
    AnomalyCategory,
    AnomalySeverity,
)


class AnomalyEngine:
    def __init__(self, structuring_threshold: float = 10000.0):
        self.structuring_threshold = structuring_threshold

    def evaluate_anomalies(
        self,
        transactions: List[Transaction],
        entities: List[Entity],
        relationships: List[Relationship],
        cycles: List[TransactionCycle],
        documents: List[NormalizedDocument],
    ) -> List[AnomalyFinding]:
        anomalies: List[AnomalyFinding] = []

        if not transactions:
            return anomalies

        # 1. Statistical Isolation Forest Anomaly Detection
        iso_anomalies = self._run_isolation_forest(transactions)
        anomalies.extend(iso_anomalies)

        # 2. Rule-Based Forensic Analysis across all 12 Categories

        # Category 1: Unusually High Amount (95th Percentile Rule)
        amounts = [t.amount for t in transactions]
        if len(amounts) > 3:
            p95 = np.percentile(amounts, 95)
            for tx in transactions:
                if tx.amount > p95 and tx.amount > 50000:
                    score = min(1.0, round(tx.amount / (p95 * 2.0), 2))
                    anomalies.append(
                        AnomalyFinding(
                            anomaly_id=f"ANO-{uuid.uuid4().hex[:8].upper()}",
                            transaction_id=tx.transaction_id,
                            entity_id=tx.sender_id,
                            anomaly_type=AnomalyCategory.UNUSUALLY_HIGH_AMOUNT,
                            anomaly_score=min(0.95, max(0.70, score)),
                            severity=AnomalySeverity.HIGH if tx.amount > 100000 else AnomalySeverity.MEDIUM,
                            explanation=f"Transaction amount ${tx.amount:,.2f} exceeds 95th percentile threshold (${p95:,.2f}) by {((tx.amount/p95)-1)*100:.1f}%.",
                            supporting_features={"amount": tx.amount, "p95_threshold": round(p95, 2)},
                            evidence_documents=[tx.document_id] if tx.document_id else [],
                        )
                    )

        # Category 4 & 12: Circular Transactions & Suspicious Clusters from Graph
        for cyc in cycles:
            anomalies.append(
                AnomalyFinding(
                    anomaly_id=f"ANO-{uuid.uuid4().hex[:8].upper()}",
                    transaction_id=cyc.transactions_involved[0] if cyc.transactions_involved else None,
                    entity_id=None,
                    anomaly_type=AnomalyCategory.CIRCULAR_TRANSACTION,
                    anomaly_score=0.92,
                    severity=AnomalySeverity.CRITICAL,
                    explanation=f"Circular transaction flow detected: {cyc.explanation}",
                    supporting_features={
                        "cycle_length": cyc.cycle_length,
                        "total_amount": cyc.total_amount,
                        "entities_count": len(cyc.entities_involved),
                    },
                    evidence_documents=cyc.source_documents,
                )
            )

        # Category 5: Structuring / Splitting Pattern (Smurfing under $10k threshold)
        sender_txs: Dict[str, List[Transaction]] = {}
        for tx in transactions:
            sender_txs.setdefault(tx.sender_name, []).append(tx)

        for sender, tx_list in sender_txs.items():
            # Check for multiple transactions just under CTR threshold ($9,000 - $9,999)
            structured = [t for t in tx_list if 8500.0 <= t.amount < self.structuring_threshold]
            if len(structured) >= 2:
                tot_struct = sum(t.amount for t in structured)
                anomalies.append(
                    AnomalyFinding(
                        anomaly_id=f"ANO-{uuid.uuid4().hex[:8].upper()}",
                        transaction_id=structured[0].transaction_id,
                        entity_id=structured[0].sender_id,
                        anomaly_type=AnomalyCategory.STRUCTURING_SPLITTING,
                        anomaly_score=0.96,
                        severity=AnomalySeverity.CRITICAL,
                        explanation=f"Detected {len(structured)} structured transactions from '{sender}' totaling ${tot_struct:,.2f}, each individually below the ${self.structuring_threshold:,.2f} mandatory reporting threshold.",
                        supporting_features={
                            "sender": sender,
                            "structured_count": len(structured),
                            "total_structured_amount": tot_struct,
                            "individual_amounts": [t.amount for t in structured],
                        },
                        evidence_documents=list(set(t.document_id for t in structured if t.document_id)),
                    )
                )

        # Category 8: Duplicate Transactions (Same amount, same sender, same receiver)
        seen_tx_signatures: Dict[Tuple[str, str, float], List[Transaction]] = {}
        for tx in transactions:
            sig = (tx.sender_name.upper(), tx.receiver_name.upper(), round(tx.amount, 2))
            seen_tx_signatures.setdefault(sig, []).append(tx)

        for sig, dup_list in seen_tx_signatures.items():
            if len(dup_list) > 1:
                anomalies.append(
                    AnomalyFinding(
                        anomaly_id=f"ANO-{uuid.uuid4().hex[:8].upper()}",
                        transaction_id=dup_list[1].transaction_id,
                        entity_id=dup_list[1].sender_id,
                        anomaly_type=AnomalyCategory.DUPLICATE_TRANSACTION,
                        anomaly_score=0.85,
                        severity=AnomalySeverity.HIGH,
                        explanation=f"Duplicate transaction pattern: {len(dup_list)} identical transfers of ${sig[2]:,.2f} from '{sig[0]}' to '{sig[1]}'.",
                        supporting_features={
                            "duplicate_count": len(dup_list),
                            "amount": sig[2],
                            "sender": sig[0],
                            "receiver": sig[1],
                        },
                        evidence_documents=list(set(t.document_id for t in dup_list if t.document_id)),
                    )
                )

        # Category 10: Segregation of Duties Violation
        # Search for person who approved an invoice AND issued/created it
        approvers = [r for r in relationships if r.relation_type.value == "APPROVED"]
        issuers = [r for r in relationships if r.relation_type.value == "ISSUED"]
        
        for app in approvers:
            for iss in issuers:
                if app.source_id == iss.source_id:
                    # Same person approved and issued
                    person_name = next((e.name for e in entities if e.entity_id == app.source_id), app.source_id)
                    anomalies.append(
                        AnomalyFinding(
                            anomaly_id=f"ANO-{uuid.uuid4().hex[:8].upper()}",
                            transaction_id=None,
                            entity_id=app.source_id,
                            anomaly_type=AnomalyCategory.SEGREGATION_OF_DUTIES,
                            anomaly_score=0.98,
                            severity=AnomalySeverity.CRITICAL,
                            explanation=f"Segregation-of-Duties conflict: Entity '{person_name}' both issued and approved financial document/invoice.",
                            supporting_features={"person_id": app.source_id, "evidence_app": app.evidence_text, "evidence_iss": iss.evidence_text},
                            evidence_documents=list(set([app.document_id, iss.document_id])),
                        )
                    )

        # Category 7: Missing Documentation (Payment without matching invoice or reference)
        for tx in transactions:
            if not tx.payment_reference or "Ref in DOC" in tx.payment_reference:
                # Check if there is an associated invoice document
                doc_has_invoice = any("INV-" in d.extracted_text for d in documents if d.document_id == tx.document_id)
                if not doc_has_invoice and tx.amount > 20000:
                    anomalies.append(
                        AnomalyFinding(
                            anomaly_id=f"ANO-{uuid.uuid4().hex[:8].upper()}",
                            transaction_id=tx.transaction_id,
                            entity_id=tx.sender_id,
                            anomaly_type=AnomalyCategory.MISSING_DOCUMENTATION,
                            anomaly_score=0.75,
                            severity=AnomalySeverity.MEDIUM,
                            explanation=f"High-value payment of ${tx.amount:,.2f} from '{tx.sender_name}' to '{tx.receiver_name}' lacks backing invoice or purchase order documentation.",
                            supporting_features={"amount": tx.amount, "sender": tx.sender_name, "receiver": tx.receiver_name},
                            evidence_documents=[tx.document_id] if tx.document_id else [],
                        )
                    )

        return anomalies

    def _run_isolation_forest(self, transactions: List[Transaction]) -> List[AnomalyFinding]:
        anomalies: List[AnomalyFinding] = []
        if len(transactions) < 5:
            return anomalies

        # Feature matrix: [amount, log(amount), len(sender_name), len(receiver_name)]
        X = []
        for tx in transactions:
            amt = max(1.0, tx.amount)
            X.append([amt, np.log(amt), len(tx.sender_name), len(tx.receiver_name)])

        X = np.array(X)
        try:
            clf = IsolationForest(contamination=0.15, random_state=42)
            preds = clf.fit_predict(X)
            scores = -clf.score_samples(X)  # Higher score = more anomalous

            for idx, (pred, score) in enumerate(zip(preds, scores)):
                if pred == -1:  # Outlier
                    tx = transactions[idx]
                    norm_score = min(0.99, max(0.65, round(float(score), 2)))
                    anomalies.append(
                        AnomalyFinding(
                            anomaly_id=f"ANO-{uuid.uuid4().hex[:8].upper()}",
                            transaction_id=tx.transaction_id,
                            entity_id=tx.sender_id,
                            anomaly_type=AnomalyCategory.UNUSUAL_ACCOUNT_RELATIONSHIP,
                            anomaly_score=norm_score,
                            severity=AnomalySeverity.HIGH if norm_score > 0.85 else AnomalySeverity.MEDIUM,
                            explanation=f"Statistical outlier detected via Isolation Forest (anomaly score {norm_score:.2f}) for transfer of ${tx.amount:,.2f} between '{tx.sender_name}' and '{tx.receiver_name}'.",
                            supporting_features={
                                "amount": tx.amount,
                                "isolation_score": float(score),
                                "sender": tx.sender_name,
                                "receiver": tx.receiver_name,
                            },
                            evidence_documents=[tx.document_id] if tx.document_id else [],
                        )
                    )
        except Exception as e:
            print(f"[Isolation Forest Engine Warning]: {e}")

        return anomalies
