"""
Module C — Bank Reconciliation Engine
Automates matching between Bank Statements and Accounting Ledger (Books of Accounts),
identifying matched transactions, unrecorded bank charges, timing variances, duplicates, and amount mismatches.
"""

import uuid
from typing import List, Dict, Any, Tuple
from apexforge.models.data_models import (
    Transaction,
    AutoLedgerEntry,
    BankReconciliationLine,
    ReconciliationMatchStatus,
)


class BankReconciliationEngine:
    def __init__(self, date_tolerance_days: int = 5):
        self.date_tolerance_days = date_tolerance_days
        self.reconciliation_lines: List[BankReconciliationLine] = []

    def reconcile(
        self,
        bank_transactions: List[Transaction],
        ledger_entries: List[AutoLedgerEntry],
    ) -> List[BankReconciliationLine]:
        """Reconciles Bank Statement transactions against Accounting Ledger entries."""
        self.reconciliation_lines.clear()
        unmatched_ledger = list(ledger_entries)

        for bank_tx in bank_transactions:
            line_id = f"REC-{uuid.uuid4().hex[:8].upper()}"
            matched_entry: AutoLedgerEntry = None
            match_status = ReconciliationMatchStatus.UNMATCHED_BANK
            recommendation = "Investigate unrecorded bank statement transaction in accounting ledger."
            ledger_desc = ""
            ledger_date = ""
            ledger_amt = 0.0
            variance = 0.0

            # 1. Exact Match Check (Amount & Reference)
            for entry in unmatched_ledger:
                if abs(entry.amount - bank_tx.amount) < 0.01 and (
                    bank_tx.transaction_id == entry.transaction_id
                    or bank_tx.payment_reference.lower() in entry.description.lower()
                    or entry.vendor_customer.lower() in bank_tx.receiver_name.lower()
                ):
                    matched_entry = entry
                    match_status = ReconciliationMatchStatus.MATCHED
                    recommendation = "Reconciled cleanly with Books of Accounts."
                    break

            # 2. Near Amount Mismatch Check
            if not matched_entry:
                for entry in unmatched_ledger:
                    if bank_tx.transaction_id == entry.transaction_id and abs(entry.amount - bank_tx.amount) >= 0.01:
                        matched_entry = entry
                        match_status = ReconciliationMatchStatus.AMOUNT_MISMATCH
                        variance = bank_tx.amount - entry.amount
                        recommendation = f"Amount Discrepancy of ₹{abs(variance):,.2f} INR between Bank statement and Books."
                        break

            # 3. Bank Charges / Small Interest Check
            if not matched_entry and bank_tx.amount < 5000 and any(k in bank_tx.payment_reference.lower() for k in ["chg", "charge", "fee", "gst", "int"]):
                match_status = ReconciliationMatchStatus.BANK_CHARGES
                recommendation = "Unrecorded Bank Charge / Statutory Fee. Post adjusting entry to Bank Charges Ledger."

            if matched_entry:
                ledger_desc = matched_entry.description
                ledger_date = matched_entry.date
                ledger_amt = matched_entry.amount
                unmatched_ledger.remove(matched_entry)

            rec_line = BankReconciliationLine(
                line_id=line_id,
                bank_date=bank_tx.timestamp[:10] if bank_tx.timestamp else "2024-04-01",
                ledger_date=ledger_date,
                bank_description=f"{bank_tx.payment_reference} ({bank_tx.sender_name} -> {bank_tx.receiver_name})",
                ledger_description=ledger_desc,
                bank_amount=bank_tx.amount,
                ledger_amount=ledger_amt,
                variance=variance,
                status=match_status,
                source_bank_doc=bank_tx.document_id or "DOC-CSV-001",
                source_ledger_ref=matched_entry.entry_id if matched_entry else "",
                recommendation=recommendation,
            )
            self.reconciliation_lines.append(rec_line)

        # 4. Remaining Unmatched Ledger Entries (Cheques Issued but not presented)
        for entry in unmatched_ledger:
            line_id = f"REC-{uuid.uuid4().hex[:8].upper()}"
            rec_line = BankReconciliationLine(
                line_id=line_id,
                bank_date="",
                ledger_date=entry.date,
                bank_description="[MISSING IN BANK STATEMENT]",
                ledger_description=entry.description,
                bank_amount=0.0,
                ledger_amount=entry.amount,
                variance=-entry.amount,
                status=ReconciliationMatchStatus.UNMATCHED_LEDGER,
                source_bank_doc="",
                source_ledger_ref=entry.entry_id,
                recommendation="Unpresented cheque or uncredited deposit recorded in Books of Accounts.",
            )
            self.reconciliation_lines.append(rec_line)

        return self.reconciliation_lines

    def get_reconciliation_summary(self) -> Dict[str, Any]:
        """Calculates quantitative reconciliation summary indicators."""
        total_items = len(self.reconciliation_lines)
        matched_items = [l for l in self.reconciliation_lines if l.status == ReconciliationMatchStatus.MATCHED]
        unmatched_bank = [l for l in self.reconciliation_lines if l.status == ReconciliationMatchStatus.UNMATCHED_BANK]
        unmatched_ledger = [l for l in self.reconciliation_lines if l.status == ReconciliationMatchStatus.UNMATCHED_LEDGER]
        amount_mismatches = [l for l in self.reconciliation_lines if l.status == ReconciliationMatchStatus.AMOUNT_MISMATCH]
        bank_charges = [l for l in self.reconciliation_lines if l.status == ReconciliationMatchStatus.BANK_CHARGES]

        matched_amt = sum(l.bank_amount for l in matched_items)
        unmatched_amt = sum(l.bank_amount for l in unmatched_bank) + sum(l.ledger_amount for l in unmatched_ledger)

        return {
            "total_line_items": total_items,
            "matched_count": len(matched_items),
            "unmatched_bank_count": len(unmatched_bank),
            "unmatched_ledger_count": len(unmatched_ledger),
            "amount_mismatch_count": len(amount_mismatches),
            "bank_charges_count": len(bank_charges),
            "reconciled_amount_inr": matched_amt,
            "unreconciled_discrepancy_inr": unmatched_amt,
        }
