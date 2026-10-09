"""
Sample Data Exporter for ApexForge Platform
Generates realistic financial evidence files (.CSV, .TXT, .JSON, .EML, .XLSX) in the `sample_data/` directory
for upload and testing in the ApexForge Multi-File Ingestion tab.
"""

import os
import json
import pandas as pd
from pathlib import Path

# Target directory
BASE_DIR = Path(__file__).resolve().parent
SAMPLE_DIR = BASE_DIR / "sample_data"
SAMPLE_DIR.mkdir(exist_ok=True)

print(f"Generating sample data files in: {SAMPLE_DIR}")

# 1. Bank Statement CSV (bank_statement_fy2024_25.csv)
csv_content = """Date,Sender,Receiver,Amount,Currency,Reference
2026-03-01,Shell Corp India Pvt Ltd,Vanguard Trading India Pvt Ltd,13500000.00,INR,NEFT Wire Transfer Ref #STR-1001 (CGST Sec 16(2) Loop)
2026-03-02,Vanguard Trading India Pvt Ltd,Horizon Holdings India Pvt Ltd,13500000.00,INR,RTGS Payment Ref #STR-1002 (CGST Sec 16(2) Loop)
2026-03-03,Horizon Holdings India Pvt Ltd,Shell Corp India Pvt Ltd,13500000.00,INR,Consulting Fee Ref #STR-1003 (CGST Sec 16(2) Loop)
2026-03-04,Ramesh Kumar (Director),Offshore Trust Account ACCT-8891,45000.00,INR,Hand Cash Loan Deposit Sec 269SS
2026-03-04,Ramesh Kumar (Director),Offshore Trust Account ACCT-8891,9500.00,INR,Tranche B Cash Deposit
2026-03-05,Ramesh Kumar (Director),Offshore Trust Account ACCT-8891,9750.00,INR,Tranche C Cash Deposit
2026-03-06,Apex Global Corp India Pvt Ltd,Vanguard Trading India Pvt Ltd,1250000.00,INR,Vendor Invoice #INV-2026-889 (Works Contract Sec 194C)
2026-03-07,Apex Global Corp India Pvt Ltd,Vanguard Trading India Pvt Ltd,1250000.00,INR,Vendor Invoice #INV-2026-889 (Duplicate Entry)
2026-03-08,Apex Global Corp India Pvt Ltd,Apex Logistics India,25000.00,INR,Courier Vendor Expense Cash Payment Sec 40A(3) Disallowance
2026-03-09,Apex Global Corp India Pvt Ltd,Legal Firm & Co India,150000.00,INR,Legal Professional Fees Sec 194J
2026-03-10,Vanguard Trading India Pvt Ltd,Apex Global Corp India Pvt Ltd,45000000.00,INR,Unbacked Bulk Transfer Sec 68 Unexplained Income
2026-03-11,Apex Global Corp India Pvt Ltd,Commercial Premises Pvt Ltd,350000.00,INR,Office Rent Payment Sec 194I
2026-03-12,Horizon Holdings India Pvt Ltd,Offshore Bank US98BANK0012,8800000.00,INR,Offshore Wire Transfer Sec 195
2026-03-13,Priya Sharma,Apex Global Corp India Pvt Ltd,50000.00,INR,Expense Reimbursement
2026-03-14,Tech Solutions India LLP,Vanguard Trading India Pvt Ltd,670000.00,INR,Services Rendered
"""

with open(SAMPLE_DIR / "bank_statement_fy2024_25.csv", "w", encoding="utf-8") as f:
    f.write(csv_content)

# 2. General Ledger CSV (books_ledger_fy2024_25.csv)
ledger_df = pd.DataFrame([
    {"Date": "2026-03-01", "Voucher_No": "VOUCH-101", "Particulars": "Vanguard Trading India Pvt Ltd", "Debit_Account": "Purchase Account", "Credit_Account": "HDFC Bank A/C 9901", "Amount_INR": 13500000.00, "GSTIN": "27AAACV1234F1Z1", "TDS_Section": "Sec 194Q"},
    {"Date": "2026-03-06", "Voucher_No": "VOUCH-102", "Particulars": "Vanguard Trading India Pvt Ltd", "Debit_Account": "Works Contract Expense", "Credit_Account": "HDFC Bank A/C 9901", "Amount_INR": 1250000.00, "GSTIN": "27AAACV1234F1Z1", "TDS_Section": "Sec 194C"},
    {"Date": "2026-03-08", "Voucher_No": "VOUCH-103", "Particulars": "Apex Logistics India", "Debit_Account": "Freight & Courier Charges", "Credit_Account": "Cash Account", "Amount_INR": 25000.00, "GSTIN": "07AAAAA1002A1Z5", "TDS_Section": "N/A"},
    {"Date": "2026-03-09", "Voucher_No": "VOUCH-104", "Particulars": "Legal Firm & Co India", "Debit_Account": "Legal & Professional Fees", "Credit_Account": "HDFC Bank A/C 9901", "Amount_INR": 150000.00, "GSTIN": "07AAAAA1003A1Z5", "TDS_Section": "Sec 194J"},
    {"Date": "2026-03-11", "Voucher_No": "VOUCH-105", "Particulars": "Commercial Premises Pvt Ltd", "Debit_Account": "Rent Expense", "Credit_Account": "HDFC Bank A/C 9901", "Amount_INR": 350000.00, "GSTIN": "27AAACC5555K1Z2", "TDS_Section": "Sec 194I"},
])
ledger_df.to_csv(SAMPLE_DIR / "books_ledger_fy2024_25.csv", index=False)

# Excel version as well
ledger_df.to_excel(SAMPLE_DIR / "books_ledger_fy2024_25.xlsx", index=False)

# 3. Income Tax AIS & Form 26AS CSV (income_tax_ais_form26as.csv)
ais_df = pd.DataFrame([
    {"PAN": "AAACA1234F", "FY": "2024-25", "Info_Code": "TDS-194C", "Description": "Payments to Contractors", "Reporter": "Vanguard Trading India Pvt Ltd", "Reported_Amount_INR": 13500000.00, "TDS_Deducted": 270000.00},
    {"PAN": "AAACA1234F", "FY": "2024-25", "Info_Code": "SFT-005", "Description": "Interest on Fixed Deposit", "Reporter": "HDFC Bank Ltd", "Reported_Amount_INR": 850000.00, "TDS_Deducted": 85000.00},
    {"PAN": "AAACA1234F", "FY": "2024-25", "Info_Code": "TDS-194J", "Description": "Professional Fees", "Reporter": "Apex Global Corp India Pvt Ltd", "Reported_Amount_INR": 1200000.00, "TDS_Deducted": 120000.00},
    {"PAN": "AAACA1234F", "FY": "2024-25", "Info_Code": "SFT-014", "Description": "Sale of Securities", "Reporter": "National Stock Exchange India", "Reported_Amount_INR": 4500000.00, "TDS_Deducted": 0.0},
])
ais_df.to_csv(SAMPLE_DIR / "income_tax_ais_form26as.csv", index=False)

# 4. Tax Invoice Text Document (tax_invoice_INV_2026_889.txt)
inv_text = """==================================================
TAX INVOICE: INV-2026-889
==================================================
Date: 2026-03-01
Issuer / Creator: Rajesh Sharma
GSTIN: 27AAACV1234F1Z1 | PAN: AAACV1234F
Vendor: Vanguard Trading India Pvt Ltd
Billed To: Apex Global Corp India Pvt Ltd
Total Amount: ₹12,50,000.00 INR
CGST (9%): ₹1,12,500.00 | SGST (9%): ₹1,12,500.00
Description: Professional Works Contract & Maintenance Services
Payment Status: PAID via NEFT
Notes: Approved by Rajesh Sharma on 2026-03-05 (Segregation of Duties Conflict)
=================================================="""

with open(SAMPLE_DIR / "tax_invoice_INV_2026_889.txt", "w", encoding="utf-8") as f:
    f.write(inv_text)

# 5. Email Evidence Record (.eml)
eml_text = """From: ramesh.kumar@apexglobal.in
To: ca.audit@taxconsultants.in
Date: 2026-03-04 10:30:00 IST
Subject: Hand Cash Deposit & Circular Routing Confirmation

Dear Audit Team,

Please note the hand cash deposit of ₹45,000.00 INR loan into Offshore Trust Account ACCT-8891.
Also confirm receipt of ₹1,35,00,000.00 INR round-trip transfer from Shell Corp India Pvt Ltd to Vanguard Trading India Pvt Ltd.

Regards,
Ramesh Kumar
Director, Apex Global Corp India Pvt Ltd
"""

with open(SAMPLE_DIR / "audit_evidence_email.eml", "w", encoding="utf-8") as f:
    f.write(eml_text)

# 6. JSON Invoice Payload (invoice_batch.json)
json_data = [
    {
        "invoice_number": "INV-2026-901",
        "date": "2026-03-10",
        "vendor_name": "Tech Solutions India LLP",
        "client_name": "Apex Global Corp India Pvt Ltd",
        "gstin": "07AAAAA1001A1Z5",
        "pan": "AAAAA1001A",
        "total_amount_inr": 320000.0,
        "items": [
            {"description": "Annual ERP Software Subscription", "rate": 320000.0, "tax_rate": 18.0}
        ],
        "status": "APPROVED",
    },
    {
        "invoice_number": "INV-2026-902",
        "date": "2026-03-12",
        "vendor_name": "Commercial Premises Pvt Ltd",
        "client_name": "Apex Global Corp India Pvt Ltd",
        "gstin": "27AAACC5555K1Z2",
        "pan": "AAACC5555K",
        "total_amount_inr": 350000.0,
        "items": [
            {"description": "Office Building Monthly Lease", "rate": 350000.0, "tax_rate": 18.0}
        ],
        "status": "PAID",
    }
]

with open(SAMPLE_DIR / "invoice_batch.json", "w", encoding="utf-8") as f:
    json.dump(json_data, f, indent=2)

print("Sample data generation completed successfully!")
