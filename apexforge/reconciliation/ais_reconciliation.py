"""
Module D — Income Tax AIS & Form 26AS Reconciliation Engine
Reconciles Income Tax AIS (Annual Information Statement) & Form 26AS against Books & Bank transactions,
identifying unreported income (Sec 68/115BBE), short TDS deductions (Sec 40(a)(ia)), and cash limit violations (Sec 40A(3), Sec 269SS).
"""

import uuid
from typing import List, Dict, Any, Optional
from apexforge.models.data_models import Transaction, AutoLedgerEntry, AISRecord, AuditReviewStatus


class AISReconciliationEngine:
    def __init__(self, pan: str = "AAACA1234F", financial_year: str = "FY 2024-25"):
        self.pan = pan
        self.financial_year = financial_year
        self.ais_records: List[AISRecord] = []

    def build_synthetic_ais_dataset(self, transactions: List[Transaction]) -> List[AISRecord]:
        """
        Generates realistic AIS records corresponding to the transaction set
        to allow direct, seamless reconciliation against Books & Bank statements.
        """
        records: List[AISRecord] = []
        
        # 1. AIS Record for High-Value Sales / Receipts (SFT-014 / TDS-194C)
        records.append(
            AISRecord(
                record_id=f"AIS-{uuid.uuid4().hex[:8].upper()}",
                pan=self.pan,
                financial_year=self.financial_year,
                info_code="TDS-194C",
                info_description="Payments to Contractors / Works Contracts",
                source_reporter="Vanguard Trading India Pvt Ltd",
                reported_amount=13500000.0,
                book_recorded_amount=13500000.0,
                variance_amount=0.0,
                disallowance_section="CGST Sec 16(2) / Income Tax Sec 40(a)(ia)",
                compliance_risk="NORMAL",
                status=AuditReviewStatus.OPEN,
                evidence_ref="Form 26AS Part A / AIS SFT-014",
            )
        )

        # 2. AIS Record for Unreported Interest / High-Value FD (SFT-005) - Mismatch Case
        records.append(
            AISRecord(
                record_id=f"AIS-{uuid.uuid4().hex[:8].upper()}",
                pan=self.pan,
                financial_year=self.financial_year,
                info_code="SFT-005",
                info_description="Interest on Fixed Deposit & Savings Account",
                source_reporter="HDFC Bank Ltd (GSTIN: 27AAACH1822AA1Z)",
                reported_amount=850000.0,
                book_recorded_amount=0.0,  # Unreported in Books!
                variance_amount=850000.0,
                disallowance_section="Sec 68 / Sec 115BBE (Unexplained Income @ 78%)",
                compliance_risk="HIGH_RISK",
                status=AuditReviewStatus.OPEN,
                evidence_ref="AIS SFT-005 / Form 26AS Part B",
            )
        )

        # 3. AIS Record for Professional Fees TDS (TDS-194J)
        records.append(
            AISRecord(
                record_id=f"AIS-{uuid.uuid4().hex[:8].upper()}",
                pan=self.pan,
                financial_year=self.financial_year,
                info_code="TDS-194J",
                info_description="Fees for Technical & Professional Services",
                source_reporter="Apex Global Corp India Pvt Ltd",
                reported_amount=1200000.0,
                book_recorded_amount=1200000.0,
                variance_amount=0.0,
                disallowance_section="Sec 194J (10% TDS Deducted)",
                compliance_risk="NORMAL",
                status=AuditReviewStatus.OPEN,
                evidence_ref="Form 26AS Part A1",
            )
        )

        # 4. AIS Record for High-Value Securities Transactions (SFT-014)
        records.append(
            AISRecord(
                record_id=f"AIS-{uuid.uuid4().hex[:8].upper()}",
                pan=self.pan,
                financial_year=self.financial_year,
                info_code="SFT-014",
                info_description="Sale of Listed Shares / Mutual Funds",
                source_reporter="National Stock Exchange India Ltd",
                reported_amount=4500000.0,
                book_recorded_amount=2000000.0,  # Partial recording mismatch
                variance_amount=2500000.0,
                disallowance_section="Sec 45 / Capital Gains Shortfall & Sec 115BBE",
                compliance_risk="HIGH_RISK",
                status=AuditReviewStatus.OPEN,
                evidence_ref="AIS SFT-014 / Broker Transaction Statement",
            )
        )

        self.ais_records = records
        return self.ais_records

    def reconcile_with_books(
        self,
        ledger_entries: List[AutoLedgerEntry],
        bank_transactions: List[Transaction],
    ) -> List[AISRecord]:
        """Reconciles AIS records against recorded Books of Accounts and Bank Statements."""
        if not self.ais_records:
            self.build_synthetic_ais_dataset(bank_transactions)

        for record in self.ais_records:
            total_book_matching = 0.0
            for entry in ledger_entries:
                if (
                    record.source_reporter.lower() in entry.vendor_customer.lower()
                    or record.source_reporter.lower() in entry.description.lower()
                    or (record.info_code in entry.tds_section)
                ):
                    total_book_matching += entry.amount

            if total_book_matching > 0:
                record.book_recorded_amount = total_book_matching
                record.variance_amount = abs(record.reported_amount - total_book_matching)
                if record.variance_amount > 10000:
                    record.compliance_risk = "HIGH_RISK" if record.variance_amount > 500000 else "MEDIUM_RISK"

        return self.ais_records

    def get_ais_summary(self) -> Dict[str, Any]:
        """Summarizes AIS reconciliation findings and statutory risks."""
        total_reported = sum(r.reported_amount for r in self.ais_records)
        total_books = sum(r.book_recorded_amount for r in self.ais_records)
        high_risk_records = [r for r in self.ais_records if r.compliance_risk == "HIGH_RISK"]
        total_unreported_variance = sum(r.variance_amount for r in high_risk_records)

        return {
            "pan": self.pan,
            "financial_year": self.financial_year,
            "total_ais_records": len(self.ais_records),
            "total_reported_amount_inr": total_reported,
            "total_book_recorded_inr": total_books,
            "high_risk_discrepancies": len(high_risk_records),
            "unreported_income_variance_inr": total_unreported_variance,
        }
