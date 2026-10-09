"""
Module B — AI Automatic Ledger Generation Engine
Processes raw extracted transactions and document payloads to generate double-entry accounting ledger entries
with statutory GST (CGST/SGST/IGST & ITC eligibility u/s 16(2)) and TDS section mappings (194C, 194J, 194H, 194I, 194Q).
"""

import uuid
from typing import List, Dict, Any, Optional
from apexforge.models.data_models import Transaction, AutoLedgerEntry, LedgerCategory, AuditReviewStatus


class AutoLedgerGenerator:
    def __init__(self):
        self.ledger_entries: List[AutoLedgerEntry] = []

    def classify_transaction(self, tx: Transaction) -> AutoLedgerEntry:
        """Classifies a transaction into double-entry accounting ledger format with statutory tags."""
        desc_lower = (tx.payment_reference + " " + tx.evidence_text + " " + tx.sender_name + " " + tx.receiver_name).lower()
        amount = tx.amount

        # Default classification
        category = LedgerCategory.INDIRECT_EXPENSE
        debit_account = "General Expenses Ledger"
        credit_account = f"Bank Account ({tx.sender_name})"
        vendor_customer = tx.receiver_name
        gst_rate = 18.0
        itc_eligible = True
        tds_section = ""
        confidence = 0.94

        # Rule & Keyword based AI classification logic tuned to Indian Accounting Standards (AS / Ind AS)
        if any(k in desc_lower for k in ["sales", "revenue", "invoice customer", "receipt", "customer payment"]):
            category = LedgerCategory.REVENUE_SALES
            debit_account = f"Bank / Accounts Receivable ({tx.sender_name})"
            credit_account = "Sales Revenue Account"
            vendor_customer = tx.sender_name
            gst_rate = 18.0
            itc_eligible = False  # Output tax liability, not ITC
            confidence = 0.96

        elif any(k in desc_lower for k in ["purchase", "raw material", "inventory", "goods", "supply"]):
            category = LedgerCategory.PURCHASE_EXPENSE
            debit_account = "Purchase / Direct Material Account"
            credit_account = f"Accounts Payable ({tx.receiver_name})"
            vendor_customer = tx.receiver_name
            gst_rate = 18.0
            itc_eligible = True
            if amount > 5000000:  # TDS u/s 194Q on purchase of goods > 50L
                tds_section = "Sec 194Q (Purchase of Goods > ₹50L)"
            confidence = 0.95

        elif any(k in desc_lower for k in ["consulting", "legal", "professional", "audit", "technical"]):
            category = LedgerCategory.INDIRECT_EXPENSE
            debit_account = "Legal & Professional Fees Account"
            credit_account = f"Bank Account ({tx.sender_name})"
            gst_rate = 18.0
            tds_section = "Sec 194J (Professional / Technical Fees @ 10%)"
            confidence = 0.98

        elif any(k in desc_lower for k in ["contractor", "labour", "works contract", "construction"]):
            category = LedgerCategory.PURCHASE_EXPENSE
            debit_account = "Works Contract / Job Work Expense"
            credit_account = f"Bank Account ({tx.sender_name})"
            gst_rate = 18.0
            tds_section = "Sec 194C (Payments to Contractors @ 2%)"
            confidence = 0.95

        elif any(k in desc_lower for k in ["rent", "lease", "premise"]):
            category = LedgerCategory.INDIRECT_EXPENSE
            debit_account = "Rent & Lease Expense Account"
            credit_account = f"Bank Account ({tx.sender_name})"
            gst_rate = 18.0
            if amount > 240000:
                tds_section = "Sec 194I (Rent on Land & Building @ 10%)"
            confidence = 0.96

        elif any(k in desc_lower for k in ["commission", "brokerage"]):
            category = LedgerCategory.INDIRECT_EXPENSE
            debit_account = "Commission & Brokerage Account"
            credit_account = f"Bank Account ({tx.sender_name})"
            gst_rate = 18.0
            if amount > 15000:
                tds_section = "Sec 194H (Commission & Brokerage @ 5%)"
            confidence = 0.94

        elif any(k in desc_lower for k in ["capital", "equipment", "machinery", "computer", "asset"]):
            category = LedgerCategory.NON_CURRENT_ASSET
            debit_account = "Plant & Machinery / Asset Account"
            credit_account = f"Bank Account ({tx.sender_name})"
            gst_rate = 18.0
            itc_eligible = True
            confidence = 0.92

        elif any(k in desc_lower for k in ["tax", "gst", "tds", "challan"]):
            category = LedgerCategory.TAX_DUTIES
            debit_account = "Statutory Tax Deposit Ledger"
            credit_account = f"Bank Account ({tx.sender_name})"
            gst_rate = 0.0
            itc_eligible = False
            confidence = 0.97

        entry_id = f"LED-{uuid.uuid4().hex[:8].upper()}"
        entry = AutoLedgerEntry(
            entry_id=entry_id,
            transaction_id=tx.transaction_id,
            date=tx.timestamp[:10] if tx.timestamp else "2024-04-01",
            description=tx.payment_reference or f"Transaction between {tx.sender_name} and {tx.receiver_name}",
            debit_account=debit_account,
            credit_account=credit_account,
            amount=tx.amount,
            currency=tx.currency,
            category=category,
            vendor_customer=vendor_customer,
            gst_rate=gst_rate,
            itc_eligible=itc_eligible,
            tds_section=tds_section,
            confidence_score=confidence,
            source_document=tx.document_id or "DOC-CSV-001",
            status=AuditReviewStatus.OPEN,
        )
        return entry

    def generate_ledger_entries(self, transactions: List[Transaction]) -> List[AutoLedgerEntry]:
        """Processes a list of transactions into classified ledger entries."""
        self.ledger_entries = [self.classify_transaction(tx) for tx in transactions]
        return self.ledger_entries

    def ca_review_entry(self, entry_id: str, new_status: AuditReviewStatus, ca_notes: str = "") -> Optional[AutoLedgerEntry]:
        """CA Review control: Accept, Edit, or Reject a ledger classification entry."""
        for entry in self.ledger_entries:
            if entry.entry_id == entry_id:
                entry.status = new_status
                entry.ca_notes = ca_notes
                return entry
        return None

    def get_summary_by_category(self) -> Dict[str, float]:
        summary: Dict[str, float] = {}
        for entry in self.ledger_entries:
            cat_name = entry.category.value
            summary[cat_name] = summary.get(cat_name, 0.0) + entry.amount
        return summary
