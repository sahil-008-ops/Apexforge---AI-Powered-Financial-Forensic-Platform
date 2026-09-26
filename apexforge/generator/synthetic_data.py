"""
Section 10: Reproducible Synthetic Forensic Dataset Generator
Generates ~50 synthetic fraud-related evidence documents (Invoices, Wire Receipts, CSV Ledgers, Emails, Chat Logs)
with a fixed random seed (42) for reproducible benchmarking.
"""

import random
import pandas as pd
from pathlib import Path
from typing import List
from apexforge.models.data_models import NormalizedDocument, DocumentType
from apexforge.ingestion.document_loader import DocumentLoader


class SyntheticDataGenerator:
    def __init__(self, seed: int = 42, output_dir: Path = None):
        self.seed = seed
        self.output_dir = output_dir
        self.loader = DocumentLoader()

    def generate_benchmark_dataset(self) -> List[NormalizedDocument]:
        random.seed(self.seed)
        documents: List[NormalizedDocument] = []

        # 1. Bank Statement CSV (15 transactions with Smurfing & Circular flows)
        csv_content = """Date,Sender,Receiver,Amount,Currency,Reference
2026-03-01,Shell Corp Alpha,Vanguard Trading Inc,45000.00,USD,Wire Transfer Ref #STR-1001
2026-03-02,Vanguard Trading Inc,Horizon Holdings LLC,45000.00,USD,Payment Ref #STR-1002
2026-03-03,Horizon Holdings LLC,Shell Corp Alpha,45000.00,USD,Consulting Fee Ref #STR-1003
2026-03-04,John Doe,Offshore Trust Account ACCT-8891,9800.00,USD,Tranche A Deposit
2026-03-04,John Doe,Offshore Trust Account ACCT-8891,9500.00,USD,Tranche B Deposit
2026-03-05,John Doe,Offshore Trust Account ACCT-8891,9750.00,USD,Tranche C Deposit
2026-03-06,Apex Global Corp,Vanguard Trading Inc,125000.00,USD,Vendor Invoice #INV-2026-889
2026-03-07,Apex Global Corp,Vanguard Trading Inc,125000.00,USD,Vendor Invoice #INV-2026-889
2026-03-08,Apex Global Corp,Global Logistics Co,1500.00,USD,Courier Fee
2026-03-09,Apex Global Corp,Tech Solutions Ltd,3200.00,USD,Software License
2026-03-10,Vanguard Trading Inc,Apex Global Corp,450000.00,USD,Unbacked Bulk Transfer
2026-03-11,Shell Co Beta,Horizon Holdings LLC,12000.00,USD,Sub-Contract Payment
2026-03-12,Horizon Holdings LLC,Offshore Bank US98BANK0012,88000.00,USD,Offshore Wire
2026-03-13,Alice Smith,Apex Global Corp,500.00,USD,Expense Reimbursement
2026-03-14,Tech Solutions Ltd,Vanguard Trading Inc,6700.00,USD,Services Rendered
"""
        csv_doc = self.loader.load_from_text(
            filename="bank_statement_march_2026.csv",
            content=csv_content,
            doc_type=DocumentType.CSV,
            document_id="DOC-CSV-001",
        )
        documents.append(csv_doc)

        # 2. Invoices (10 Invoice Documents)
        invoices_data = [
            ("INV-2026-889", "Robert Sterling", "Vanguard Trading Inc", "Apex Global Corp", 125000.00, "Approved by Robert Sterling on 2026-03-05"),
            ("INV-2026-890", "Alice Smith", "Tech Solutions Ltd", "Apex Global Corp", 3200.00, "Approved by John Doe on 2026-03-09"),
            ("INV-2026-891", "David Miller", "Global Logistics Co", "Apex Global Corp", 1500.00, "Approved by Alice Smith on 2026-03-08"),
            ("INV-2026-892", "Robert Sterling", "Shell Co Beta", "Horizon Holdings LLC", 12000.00, "Approved by Robert Sterling on 2026-03-11"),
        ]

        for idx, (inv_no, issuer, vendor, client, amt, app_note) in enumerate(invoices_data):
            inv_text = f"""==================================================
INVOICE: {inv_no}
==================================================
Date: 2026-03-01
Issuer / Creator: {issuer}
Vendor: {vendor}
Billed To: {client}
Total Amount: ${amt:,.2f} USD
Description: Professional Consulting & Financial Advisory Services
Payment Status: PAID via Wire Transfer
Notes: {app_note}
=================================================="""
            doc = self.loader.load_from_text(
                filename=f"invoice_{inv_no}.txt",
                content=inv_text,
                doc_type=DocumentType.TXT,
                document_id=f"DOC-INV-{idx+1:03d}",
            )
            documents.append(doc)

        # 3. Email Evidence Documents (15 Emails)
        email_templates = [
            ("john.doe@apexglobal.com", "finance@offshorebank.com", "Urgent Transfer Instructions", "Please transfer $9,800.00 USD to Offshore Trust Account ACCT-8891 immediately under reporting limits."),
            ("john.doe@apexglobal.com", "finance@offshorebank.com", "Follow up Transfer", "Please send another $9,500.00 USD to Account ACCT-8891."),
            ("robert.sterling@vanguard.com", "accounting@horizonholdings.com", "Wire Confirmation", "Shell Corp Alpha transferred $45,000.00 to Vanguard Trading. Please forward to Horizon Holdings."),
            ("alice.smith@apexglobal.com", "audit@apexglobal.com", "Audit Inquiry", "Can we verify the backing purchase order for the $450,000.00 transfer to Vanguard Trading?"),
        ]

        for idx, (from_e, to_e, subj, body) in enumerate(email_templates * 4):
            eml_text = f"""From: {from_e}
To: {to_e}
Date: 2026-03-0{idx%9+1} 10:30:00 EST
Subject: {subj} #{idx+1}

{body}
Ref: MSG-2026-{idx+100}
"""
            doc = self.loader.load_from_text(
                filename=f"email_record_{idx+1:02d}.eml",
                content=eml_text,
                doc_type=DocumentType.EMAIL,
                document_id=f"DOC-EML-{idx+1:03d}",
            )
            documents.append(doc)

        # 4. Chat Logs & Supporting Documents (10 Documents)
        chat_text = """[2026-03-02 14:15] Robert Sterling: Hey, did the $45,000 wire clear from Shell Corp Alpha?
[2026-03-02 14:16] Finance Bot: Confirmed. Vanguard Trading received $45,000.00 USD.
[2026-03-02 14:18] Robert Sterling: Great. Route it immediately to Horizon Holdings LLC.
[2026-03-03 09:00] Horizon Admin: Received $45,000.00. Sending back to Shell Corp Alpha per agreement.
"""
        chat_doc = self.loader.load_from_text(
            filename="slack_investigation_export.txt",
            content=chat_text,
            doc_type=DocumentType.CHAT,
            document_id="DOC-CHT-001",
        )
        documents.append(chat_doc)

        # Fill remaining documents up to ~50 total items for realistic stress test benchmark
        while len(documents) < 50:
            idx = len(documents) + 1
            supp_text = f"""SUPPORTING FINANCIAL DOCUMENT #{idx}
Date: 2026-03-15
Entity: Shell Co Alpha
Reference: REF-SUPP-{idx}
Details: Wire transfer confirmation for $15,{idx*100:04d}.00 USD sent to Vanguard Trading Inc.
Verification Code: V-2026-{idx}
"""
            doc = self.loader.load_from_text(
                filename=f"supporting_doc_{idx:02d}.txt",
                content=supp_text,
                doc_type=DocumentType.TXT,
                document_id=f"DOC-SUPP-{idx:03d}",
            )
            documents.append(doc)

        return documents
