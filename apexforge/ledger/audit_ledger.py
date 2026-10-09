"""
Section 9: Forensic Reasoning Ledger
Tamper-evident, court-oriented audit ledger utilizing SHA3-256 hash chaining to ensure total integrity of investigation steps.
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple, Optional
from apexforge.models.data_models import LedgerEntry, AuditEvent, AuditReviewStatus


class ForensicAuditLedger:
    GENESIS_HASH = "0" * 64

    def __init__(self):
        self.chain: List[LedgerEntry] = []
        self.event_chain: List[AuditEvent] = []

    def compute_entry_hash(
        self,
        event_id: str,
        timestamp: str,
        event_type: str,
        actor: str,
        input_reference: str,
        finding: str,
        evidence: List[str],
        previous_hash: str,
    ) -> str:
        """Calculates SHA3-256 hash across all entry fields and previous block hash."""
        sorted_evidence = sorted(evidence)
        payload = {
            "event_id": event_id,
            "timestamp": timestamp,
            "event_type": event_type,
            "actor": actor,
            "input_reference": input_reference,
            "finding": finding,
            "evidence": sorted_evidence,
            "previous_hash": previous_hash,
        }
        serialized = json.dumps(payload, sort_keys=True)
        return hashlib.sha3_256(serialized.encode("utf-8")).hexdigest()

    def compute_event_hash(
        self,
        event_id: str,
        timestamp: str,
        user_id: str,
        action: str,
        entity_type: str,
        entity_id: str,
        previous_value: Optional[str],
        new_value: Optional[str],
        previous_hash: str,
    ) -> str:
        """Calculates SHA3-256 hash for an AuditEvent payload."""
        payload = {
            "event_id": event_id,
            "timestamp": timestamp,
            "user_id": user_id,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "previous_value": previous_value or "",
            "new_value": new_value or "",
            "previous_hash": previous_hash,
        }
        serialized = json.dumps(payload, sort_keys=True)
        return hashlib.sha3_256(serialized.encode("utf-8")).hexdigest()

    def add_entry(
        self,
        event_type: str,
        input_reference: str,
        finding: str,
        evidence: List[str] = None,
        actor: str = "ApexForge-Engine",
    ) -> LedgerEntry:
        if evidence is None:
            evidence = []

        event_id = f"EVT-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.now(timezone.utc).isoformat()

        previous_hash = self.chain[-1].current_hash if self.chain else self.GENESIS_HASH
        current_hash = self.compute_entry_hash(
            event_id=event_id,
            timestamp=timestamp,
            event_type=event_type,
            actor=actor,
            input_reference=input_reference,
            finding=finding,
            evidence=evidence,
            previous_hash=previous_hash,
        )

        entry = LedgerEntry(
            event_id=event_id,
            timestamp=timestamp,
            event_type=event_type,
            actor=actor,
            input_reference=input_reference,
            finding=finding,
            evidence=evidence,
            previous_hash=previous_hash,
            current_hash=current_hash,
        )

        self.chain.append(entry)
        return entry

    def record_event(
        self,
        action: str,
        entity_type: str,
        entity_id: str,
        user_id: str = "CA_AUDITOR_01",
        user_role: str = "Chartered Accountant / Forensic Auditor",
        previous_value: Optional[str] = None,
        new_value: Optional[str] = None,
        source: str = "System",
        ai_model: str = "Gemini-Pro-Forensic",
        confidence_score: float = 1.0,
        reason: str = "",
    ) -> AuditEvent:
        """Records a granular audit event in an append-only SHA3-256 tamper-evident chain."""
        event_id = f"AUD-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.now(timezone.utc).isoformat()
        previous_hash = self.event_chain[-1].current_hash if self.event_chain else self.GENESIS_HASH

        current_hash = self.compute_event_hash(
            event_id=event_id,
            timestamp=timestamp,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            previous_value=previous_value,
            new_value=new_value,
            previous_hash=previous_hash,
        )

        event = AuditEvent(
            event_id=event_id,
            timestamp=timestamp,
            user_id=user_id,
            user_role=user_role,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            previous_value=previous_value,
            new_value=new_value,
            source=source,
            ai_model=ai_model,
            confidence_score=confidence_score,
            previous_hash=previous_hash,
            current_hash=current_hash,
            reason=reason,
        )
        self.event_chain.append(event)
        return event

    def verify_chain_integrity(self) -> Tuple[bool, int, Optional[int], str]:
        """
        Validates the SHA3-256 hash chain for standard ledger entries.
        Returns: (is_valid, total_entries, tampered_index, explanation_message)
        """
        if not self.chain:
            return True, 0, None, "Ledger is empty. Integrity verified."

        expected_prev_hash = self.GENESIS_HASH

        for idx, entry in enumerate(self.chain):
            if entry.previous_hash != expected_prev_hash:
                return (
                    False,
                    len(self.chain),
                    idx,
                    f"TAMPER DETECTED at entry index {idx} ({entry.event_id}): previous_hash mismatch. Expected '{expected_prev_hash[:16]}...', got '{entry.previous_hash[:16]}...'",
                )

            computed_hash = self.compute_entry_hash(
                event_id=entry.event_id,
                timestamp=entry.timestamp,
                event_type=entry.event_type,
                actor=entry.actor,
                input_reference=entry.input_reference,
                finding=entry.finding,
                evidence=entry.evidence,
                previous_hash=entry.previous_hash,
            )

            if entry.current_hash != computed_hash:
                return (
                    False,
                    len(self.chain),
                    idx,
                    f"TAMPER DETECTED at entry index {idx} ({entry.event_id}): content payload hash mismatch. Data inside entry has been altered.",
                )

            expected_prev_hash = entry.current_hash

        return True, len(self.chain), None, f"Chain integrity VERIFIED across all {len(self.chain)} SHA3-256 linked ledger entries."

    def verify_event_chain_integrity(self) -> Tuple[bool, int, Optional[int], str]:
        """Validates the SHA3-256 audit event chain."""
        if not self.event_chain:
            return True, 0, None, "Event ledger is empty. Integrity verified."

        expected_prev_hash = self.GENESIS_HASH

        for idx, event in enumerate(self.event_chain):
            if event.previous_hash != expected_prev_hash:
                return (
                    False,
                    len(self.event_chain),
                    idx,
                    f"TAMPER DETECTED at event index {idx} ({event.event_id}): previous_hash mismatch.",
                )

            computed_hash = self.compute_event_hash(
                event_id=event.event_id,
                timestamp=event.timestamp,
                user_id=event.user_id,
                action=event.action,
                entity_type=event.entity_type,
                entity_id=event.entity_id,
                previous_value=event.previous_value,
                new_value=event.new_value,
                previous_hash=event.previous_hash,
            )

            if event.current_hash != computed_hash:
                return (
                    False,
                    len(self.event_chain),
                    idx,
                    f"TAMPER DETECTED at event index {idx} ({event.event_id}): content payload hash mismatch.",
                )

            expected_prev_hash = event.current_hash

        return True, len(self.event_chain), None, f"Audit event chain VERIFIED across all {len(self.event_chain)} SHA3-256 events."

    def export_ledger_dict(self) -> List[Dict[str, Any]]:
        return [entry.model_dump() for entry in self.chain]

    def export_events_dict(self) -> List[Dict[str, Any]]:
        return [event.model_dump() for event in self.event_chain]

