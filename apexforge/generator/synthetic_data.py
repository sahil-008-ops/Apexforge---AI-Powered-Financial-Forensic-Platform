"""
Section 10: Reproducible Synthetic Forensic Dataset Generator (Indian CA Tax & Forensic Accounting Benchmark)
Generates ~50 synthetic fraud-related evidence documents (Invoices, Wire Receipts, CSV Ledgers, Emails, Chat Logs)
in Indian Rupees (₹ INR) with a fixed random seed (42) for reproducible Indian CA Tax Auditing.
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

        # 1. Bank Statement CSV (15 Indian Rupee transactions with Sec 269SS, Sec 40A(3) & GST Circular flows)
        csv_content = """Date,Sender,Receiver,Amount,Currency,Reference
2026-03-01,Shell Corp India Pvt Ltd,Vanguard Trading India Pvt Ltd,4500000.00,INR,NEFT Wire Transfer Ref #STR-1001
2026-03-02,Vanguard Trading India Pvt Ltd,Horizon Holdings India Pvt Ltd,4500000.00,INR,RTGS Payment Ref #STR-1002
2026-03-03,Horizon Holdings India Pvt Ltd,Shell Corp India Pvt Ltd,4500000.00,INR,Consulting Fee Ref #STR-1003
2026-03-04,Ramesh Kumar (Director),Offshore Trust Account ACCT-8891,45000.00,INR,Hand Cash Loan Deposit Sec 269SS
2026-03-04,Ramesh Kumar (Director),Offshore Trust Account ACCT-8891,9500.00,INR,Tranche B Cash Deposit
2026-03-05,Ramesh Kumar (Director),Offshore Trust Account ACCT-8891,9750.00,INR,Tranche C Cash Deposit
2026-03-06,Apex Global India Pvt Ltd,Vanguard Trading India Pvt Ltd,1250000.00,INR,Vendor Invoice #INV-2026-889
2026-03-07,Apex Global India Pvt Ltd,Vanguard Trading India Pvt Ltd,1250000.00,INR,Vendor Invoice #INV-2026-889
2026-03-08,Apex Global India Pvt Ltd,Apex Logistics India,25000.00,INR,Courier Vendor Expense Cash Payment Sec 40A(3)
2026-03-09,Apex Global India Pvt Ltd,Tech Solutions India LLP,320000.00,INR,Software License RTGS
2026-03-10,Vanguard Trading India Pvt Ltd,Apex Global India Pvt Ltd,45000000.00,INR,Unbacked Bulk Transfer Sec 68
2026-03-11,Shell Co Beta India,Horizon Holdings India Pvt Ltd,120000.00,INR,Sub-Contract Payment
2026-03-12,Horizon Holdings India Pvt Ltd,Offshore Bank US98BANK0012,8800000.00,INR,Offshore Wire Transfer
2026-03-13,Priya Sharma,Apex Global India Pvt Ltd,50000.00,INR,Expense Reimbursement
2026-03-14,Tech Solutions India LLP,Vanguard Trading India Pvt Ltd,670000.00,INR,Services Rendered
"""
        csv_doc = self.loader.load_from_text(
            filename="bank_statement_march_2026_inr.csv",
            content=csv_content,
            doc_type=DocumentType.CSV,
            document_id="DOC-CSV-001",
        )
        documents.append(csv_doc)

        # 2. Invoices (10 Invoice Documents in ₹ INR with Tax & PAN References)
        invoices_data = [
            ("INV-2026-889", "Rajesh Sharma", "Vanguard Trading India Pvt Ltd", "Apex Global India Pvt Ltd", 1250000.00, "Approved by Rajesh Sharma on 2026-03-05 (Segregation of Duties Conflict)"),
            ("INV-2026-890", "Priya Sharma", "Tech Solutions India LLP", "Apex Global India Pvt Ltd", 320000.00, "Approved by Ramesh Kumar on 2026-03-09"),
            ("INV-2026-891", "Amit Patel", "Apex Logistics India", "Apex Global India Pvt Ltd", 25000.00, "Paid in cash currency. Approved by Priya Sharma on 2026-03-08"),
            ("INV-2026-892", "Rajesh Sharma", "Shell Co Beta India", "Horizon Holdings India Pvt Ltd", 120000.00, "Approved by Rajesh Sharma on 2026-03-11"),
        ]

        for idx, (inv_no, issuer, vendor, client, amt, app_note) in enumerate(invoices_data):
            inv_text = f"""==================================================
TAX INVOICE: {inv_no}
==================================================
Date: 2026-03-01
Issuer / Creator: {issuer}
GSTIN: 07AAAAA{idx+1000}A1Z5 | PAN: ABCDE{idx+1000}F
Vendor: {vendor}
Billed To: {client}
Total Amount: ₹{amt:,.2f} INR
Description: Professional Financial Advisory & Consulting Services
Payment Status: PAID
Notes: {app_note}
=================================================="""
            doc = self.loader.load_from_text(
                filename=f"tax_invoice_{inv_no}.txt",
                content=inv_text,
                doc_type=DocumentType.TXT,
                document_id=f"DOC-INV-{idx+1:03d}",
            )
            documents.append(doc)

        # 3. Email Evidence Documents (15 Emails)
        email_templates = [
            ("ramesh.kumar@apexglobal.in", "ca.audit@taxconsultants.in", "Cash Deposit Instruction Sec 269SS", "Please record the ₹45,000.00 INR cash deposit loan into Offshore Trust Account ACCT-8891."),
            ("ramesh.kumar@apexglobal.in", "finance@offshorebank.com", "Smurfing Cash Transfer", "Please deposit cash tranche of ₹9,500.00 INR to Account ACCT-8891."),
            ("rajesh.sharma@vanguard.in", "accounts@horizonholdings.in", "RTGS Transfer Confirmation", "Shell Corp India Pvt Ltd transferred ₹45,00,000.00 to Vanguard Trading. Please forward to Horizon Holdings."),
            ("priya.sharma@apexglobal.in", "audit@apexglobal.in", "GST ITC Verification", "Can we verify backing purchase orders and e-way bills for the ₹4,50,00,000.00 transfer to Vanguard Trading?"),
        ]

        for idx, (from_e, to_e, subj, body) in enumerate(email_templates * 4):
            eml_text = f"""From: {from_e}
To: {to_e}
Date: 2026-03-0{idx%9+1} 10:30:00 IST
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
        chat_text = """[2026-03-02 14:15] Rajesh Sharma: Did the ₹45,00,000 wire clear from Shell Corp India Pvt Ltd?
[2026-03-02 14:16] Finance Bot: Confirmed. Vanguard Trading received ₹45,00,000.00 INR.
[2026-03-02 14:18] Rajesh Sharma: Great. Route it immediately to Horizon Holdings India Pvt Ltd.
[2026-03-03 09:00] Horizon Admin: Received ₹45,00,000.00. Sending back to Shell Corp India Pvt Ltd per agreement.
"""
        chat_doc = self.loader.load_from_text(
            filename="slack_investigation_export.txt",
            content=chat_text,
            doc_type=DocumentType.CHAT,
            document_id="DOC-CHT-001",
        )
        documents.append(chat_doc)

        # Fill remaining documents up to 50 total items in ₹ INR
        while len(documents) < 50:
            idx = len(documents) + 1
            supp_text = f"""SUPPORTING AUDIT FINANCIAL DOCUMENT #{idx}
Date: 2026-03-15
Entity: Shell Corp India Pvt Ltd
Reference: REF-SUPP-{idx}
Details: Wire transfer confirmation for ₹1,50,{idx*100:03d}.00 INR sent to Vanguard Trading India Pvt Ltd.
GSTIN: 07AAAAA{idx+2000}A1Z5
"""
            doc = self.loader.load_from_text(
                filename=f"supporting_doc_{idx:02d}.txt",
                content=supp_text,
                doc_type=DocumentType.TXT,
                document_id=f"DOC-SUPP-{idx:03d}",
            )
            documents.append(doc)

        return documents
