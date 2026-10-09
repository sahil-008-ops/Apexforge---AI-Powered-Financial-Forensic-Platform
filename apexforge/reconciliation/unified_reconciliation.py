"""
Module F — Unified Multi-Way Reconciliation Engine
Integrates Bank Statements ↔ Ledger Entries ↔ AIS Tax Records ↔ Invoices ↔ Forensic Graph Cycles
into a 360-degree forensic compliance matrix.
"""

import uuid
from typing import List, Dict, Any
from apexforge.models.data_models import (
    Transaction,
    AutoLedgerEntry,
    BankReconciliationLine,
    AISRecord,
    TransactionCycle,
    UnifiedReconciliationMatrix,
)


class UnifiedReconciliationEngine:
    def __init__(self):
        self.matrix: List[UnifiedReconciliationMatrix] = []

    def build_unified_matrix(
        self,
        transactions: List[Transaction],
        ledger_entries: List[AutoLedgerEntry],
        bank_lines: List[BankReconciliationLine],
        ais_records: List[AISRecord],
        cycles: List[TransactionCycle],
    ) -> List[UnifiedReconciliationMatrix]:
        """Cross-links Bank ↔ Books ↔ AIS ↔ Invoices ↔ Graph for 360° audit transparency."""
        self.matrix.clear()
        cycle_tx_ids = set()
        for c in cycles:
            cycle_tx_ids.update(c.transactions_involved)

        for tx in transactions:
            matrix_id = f"MX-{uuid.uuid4().hex[:8].upper()}"

            # Check 1: Bank Reconciled
            bank_rec = any(
                bl.bank_amount == tx.amount or tx.payment_reference.lower() in bl.bank_description.lower()
                for bl in bank_lines
            )

            # Check 2: Ledger Posted
            ledger_posted = any(
                le.transaction_id == tx.transaction_id or le.amount == tx.amount
                for le in ledger_entries
            )

            # Check 3: AIS Matched
            ais_matched = any(
                tx.sender_name.lower() in ar.source_reporter.lower()
                or tx.receiver_name.lower() in ar.source_reporter.lower()
                for ar in ais_records
            )

            # Check 4: Invoice Backed
            invoice_backed = bool(tx.document_id and tx.document_id != "DOC-UNSUPPORTED")

            # Check 5: Graph Cycle Detected
            graph_cycle = tx.transaction_id in cycle_tx_ids or any(
                tx.sender_name in c.entities_involved for c in cycles
            )

            # Forensic Risk Calculation
            risk_score = 0.0
            if not bank_rec:
                risk_score += 0.20
            if not ledger_posted:
                risk_score += 0.20
            if not ais_matched:
                risk_score += 0.15
            if not invoice_backed:
                risk_score += 0.20
            if graph_cycle:
                risk_score += 0.25

            risk_score = min(1.0, risk_score)

            if risk_score >= 0.60:
                unified_status = "CRITICAL FORENSIC RED FLAG"
                audit_action = "Initiate Statutory Audit Note, Reverse ITC & Demand Substantive Proof"
            elif risk_score >= 0.30:
                unified_status = "MODERATE AUDIT DISCREPANCY"
                audit_action = "Obtain Management Representation & Supporting Invoices"
            else:
                unified_status = "RECONCILED & COMPLIANT"
                audit_action = "Accept Ledger Entry & Pass Working Paper Schedule"

            entry = UnifiedReconciliationMatrix(
                matrix_id=matrix_id,
                transaction_id=tx.transaction_id,
                counterparty=f"{tx.sender_name} ➔ {tx.receiver_name}",
                amount=tx.amount,
                bank_reconciled=bank_rec,
                ledger_posted=ledger_posted,
                ais_matched=ais_matched,
                invoice_backed=invoice_backed,
                graph_cycle_detected=graph_cycle,
                forensic_risk_score=risk_score,
                unified_status=unified_status,
                audit_action=audit_action,
            )
            self.matrix.append(entry)

        return self.matrix

    def get_unified_summary(self) -> Dict[str, Any]:
        """Calculates multi-way matrix summary statistics."""
        total = len(self.matrix)
        critical_flags = [m for m in self.matrix if m.forensic_risk_score >= 0.60]
        reconciled = [m for m in self.matrix if m.forensic_risk_score < 0.30]

        return {
            "total_matrix_entries": total,
            "reconciled_fully": len(reconciled),
            "critical_forensic_flags": len(critical_flags),
            "total_flagged_amount_inr": sum(m.amount for m in critical_flags),
        }
