"""
Realistic CA Audit Data Bundle Generator
Creates hyper-realistic financial evidence files exactly as Indian corporate clients provide to Chartered Accountants (CAs)
for Tax Audits (Form 3CD / u/s 44AB), Statutory Audits (Companies Act 2013), GST Audits (GSTR-9C / GSTR-2B), and Forensic Investigations.
"""

import os
import json
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CA_PACKAGE_DIR = BASE_DIR / "real_ca_audit_package"
CA_PACKAGE_DIR.mkdir(exist_ok=True)

print(f"Generating hyper-realistic CA Audit Data Bundle in: {CA_PACKAGE_DIR}")

# ==============================================================================
# 1. HDFC BANK STATEMENT (EXACT OFFICIAL CORPORATE BANKING EXPORT LAYOUT)
# ==============================================================================
hdfc_narration_header = """HDFC BANK LIMITED - CORPORATE BANKING STATEMENT
Account Name: APEX GLOBAL CORP INDIA PRIVATE LIMITED
Account Number: 50200088991122 | Currency: INR | Branch: CONNAUGHT PLACE, NEW DELHI (IFSC: HDFC0000240)
Statement Period: 01-APR-2024 to 31-MAR-2025 | Account Type: CURRENT ACCOUNT
------------------------------------------------------------------------------------------------------------------------
Date,Value Date,Transaction Description / Narration,Cheque / Ref No,Debit (INR),Credit (INR),Balance (INR)
"""

hdfc_txs = [
    ("01/04/2024", "01/04/2024", "NEFT-N091240881-SHELL CORP INDIA PVT LTD-SUPPLY OF GOODS", "NEFT-N091240881", "13500000.00", "0.00", "36500000.00"),
    ("02/04/2024", "02/04/2024", "RTGS-R091240992-VANGUARD TRADING INDIA PVT LTD-CIRCULAR SUPPLY", "RTGS-R091240992", "0.00", "13500000.00", "50000000.00"),
    ("03/04/2024", "03/04/2024", "NEFT-N091241003-HORIZON HOLDINGS INDIA PVT LTD-CONSULTING FEE", "NEFT-N091241003", "13500000.00", "0.00", "36500000.00"),
    ("05/04/2024", "05/04/2024", "CASH DEP BY RAMESH KUMAR DIR-LOAN DEPOSIT U/S 269SS", "CHQ-000182", "0.00", "45000.00", "36545000.00"),
    ("06/04/2024", "06/04/2024", "CASH WITHDRAWAL FOR PETTY EXP-TRANCHE A", "CHQ-000183", "9500.00", "0.00", "36535500.00"),
    ("07/04/2024", "07/04/2024", "CASH WITHDRAWAL FOR PETTY EXP-TRANCHE B", "CHQ-000184", "9750.00", "0.00", "36525750.00"),
    ("10/04/2024", "10/04/2024", "NEFT-N091241150-VANGUARD TRADING INDIA PVT LTD-WORKS CONTRACT", "NEFT-N091241150", "1250000.00", "0.00", "35275750.00"),
    ("12/04/2024", "12/04/2024", "CASH PMT-APEX LOGISTICS-FREIGHT CHARGES DISALLOWANCE SEC 40A(3)", "VOUCH-CASH-401", "25000.00", "0.00", "35250750.00"),
    ("15/04/2024", "15/04/2024", "RTGS-R091241288-LEGAL FIRM & CO-PROFESSIONAL FEES SEC 194J", "RTGS-R091241288", "150000.00", "0.00", "35100750.00"),
    ("20/04/2024", "20/04/2024", "NEFT-N091241390-UNACCOUNTED CASH CREDIT-VANGUARD SEC 68", "NEFT-N091241390", "0.00", "45000000.00", "80100750.00"),
    ("25/04/2024", "25/04/2024", "RTGS-R091241500-COMMERCIAL PREMISES PVT LTD-RENT SEC 194I", "RTGS-R091241500", "350000.00", "0.00", "79750750.00"),
    ("28/04/2024", "28/04/2024", "HDFC BANK CHARGES - ANNUAL LEDGER MAINTENANCE FEE + 18% GST", "SYS-CHG-9901", "2950.00", "0.00", "79747800.00"),
]

bank_file_content = hdfc_narration_header + "\n".join([",".join(t) for t in hdfc_txs])
with open(CA_PACKAGE_DIR / "HDFC_Bank_Statement_FY2024-25.csv", "w", encoding="utf-8") as f:
    f.write(bank_file_content)

# Also create TXT format mimicking official HDFC e-statement text layout
with open(CA_PACKAGE_DIR / "HDFC_Bank_Statement_FY2024-25.txt", "w", encoding="utf-8") as f:
    f.write(bank_file_content)

# ==============================================================================
# 2. TALLY PRIME DAYBOOK & GENERAL LEDGER EXPORT (EXACT TALLY FORMAT)
# ==============================================================================
tally_daybook_data = [
    {"Date": "01-04-2024", "Vch_Type": "Payment", "Vch_No": "PAY-001", "Particulars": "Shell Corp India Pvt Ltd", "Debit_Ledger": "Purchase - Raw Materials", "Credit_Ledger": "HDFC Bank A/c 991122", "Amount": 13500000.00, "GSTIN": "27AAACS1001A1Z1", "PAN": "AAACS1001A", "TDS_Sec": "Sec 194Q", "Narration": "Being raw material purchased vide Inv #INV-001"},
    {"Date": "02-04-2024", "Vch_Type": "Receipt", "Vch_No": "REC-001", "Particulars": "Vanguard Trading India Pvt Ltd", "Debit_Ledger": "HDFC Bank A/c 991122", "Credit_Ledger": "Sales Revenue Account", "Amount": 13500000.00, "GSTIN": "27AAACV1234F1Z1", "PAN": "AAACV1234F", "TDS_Sec": "N/A", "Narration": "Being sales revenue received vide RTGS"},
    {"Date": "03-04-2024", "Vch_Type": "Payment", "Vch_No": "PAY-002", "Particulars": "Horizon Holdings India Pvt Ltd", "Debit_Ledger": "Consulting Charges Ledger", "Credit_Ledger": "HDFC Bank A/c 991122", "Amount": 13500000.00, "GSTIN": "27AAACH9999K1Z5", "PAN": "AAACH9999K", "TDS_Sec": "Sec 194J", "Narration": "Being professional advisory paid vide NEFT"},
    {"Date": "05-04-2024", "Vch_Type": "Receipt", "Vch_No": "REC-002", "Particulars": "Ramesh Kumar (Director)", "Debit_Ledger": "HDFC Bank A/c 991122", "Credit_Ledger": "Unsecured Cash Loan Account", "Amount": 45000.00, "GSTIN": "UNREGISTERED", "PAN": "ABCPK1234F", "TDS_Sec": "Sec 269SS", "Narration": "Being hand cash loan deposit taken in violation of Sec 269SS"},
    {"Date": "06-04-2024", "Vch_Type": "Payment", "Vch_No": "PAY-003", "Particulars": "Petty Cash Expenses", "Debit_Ledger": "Office Expenses Ledger", "Credit_Ledger": "Cash Account", "Amount": 9500.00, "GSTIN": "N/A", "PAN": "N/A", "TDS_Sec": "N/A", "Narration": "Being petty office stationery cash payment"},
    {"Date": "10-04-2024", "Vch_Type": "Payment", "Vch_No": "PAY-004", "Particulars": "Vanguard Trading India Pvt Ltd", "Debit_Ledger": "Works Contract Expense", "Credit_Ledger": "HDFC Bank A/c 991122", "Amount": 1250000.00, "GSTIN": "27AAACV1234F1Z1", "PAN": "AAACV1234F", "TDS_Sec": "Sec 194C", "Narration": "Being works contract charges paid @ 2% TDS"},
    {"Date": "12-04-2024", "Vch_Type": "Payment", "Vch_No": "PAY-005", "Particulars": "Apex Logistics India", "Debit_Ledger": "Freight & Freight Charges", "Credit_Ledger": "Cash Account", "Amount": 25000.00, "GSTIN": "07AAAAA1002A1Z5", "PAN": "AAAAA1002A", "TDS_Sec": "N/A", "Narration": "Being cash payment for freight in violation of Sec 40A(3)"},
    {"Date": "15-04-2024", "Vch_Type": "Payment", "Vch_No": "PAY-006", "Particulars": "Legal Firm & Co India", "Debit_Ledger": "Legal & Professional Fees", "Credit_Ledger": "HDFC Bank A/c 991122", "Amount": 150000.00, "GSTIN": "07AAAAA1003A1Z5", "PAN": "AAAAA1003A", "TDS_Sec": "Sec 194J", "Narration": "Being legal fees paid with 10% TDS deducted"},
    {"Date": "20-04-2024", "Vch_Type": "Receipt", "Vch_No": "REC-003", "Particulars": "Vanguard Trading India Pvt Ltd", "Debit_Ledger": "HDFC Bank A/c 991122", "Credit_Ledger": "Unexplained Cash Credit Ledger", "Amount": 45000000.00, "GSTIN": "27AAACV1234F1Z1", "PAN": "AAACV1234F", "TDS_Sec": "Sec 68", "Narration": "Unexplained cash credit entry in books u/s 68"},
    {"Date": "25-04-2024", "Vch_Type": "Payment", "Vch_No": "PAY-007", "Particulars": "Commercial Premises Pvt Ltd", "Debit_Ledger": "Rent & Lease Expense", "Credit_Ledger": "HDFC Bank A/c 991122", "Amount": 350000.00, "GSTIN": "27AAACC5555K1Z2", "PAN": "AAACC5555K", "TDS_Sec": "Sec 194I", "Narration": "Being office rent paid @ 10% TDS"},
]

df_tally = pd.DataFrame(tally_daybook_data)
df_tally.to_excel(CA_PACKAGE_DIR / "Tally_Prime_DayBook_FY2024-25.xlsx", index=False)
df_tally.to_csv(CA_PACKAGE_DIR / "Tally_Prime_DayBook_FY2024-25.csv", index=False)

# ==============================================================================
# 3. OFFICIAL GST PORTAL GSTR-2B & GSTR-3B RECONCILIATION REPORT
# ==============================================================================
gstr2b_data = [
    {"Supplier_GSTIN": "27AAACS1001A1Z1", "Trade_Name": "Shell Corp India Pvt Ltd", "Invoice_No": "INV-001", "Invoice_Type": "Regular", "Invoice_Date": "01-04-2024", "Invoice_Value": 15930000.00, "Taxable_Value": 13500000.00, "CGST": 1215000.00, "SGST": 1215000.00, "IGST": 0.00, "GSTR_3B_Filed": "YES", "ITC_Availability": "Ineligible u/s 16(2) (Circular Trading Loop)", "Reason_For_Ineligibility": "Round-trip flow without physical supply of goods"},
    {"Supplier_GSTIN": "27AAACV1234F1Z1", "Trade_Name": "Vanguard Trading India Pvt Ltd", "Invoice_No": "INV-2026-889", "Invoice_Type": "Regular", "Invoice_Date": "10-04-2024", "Invoice_Value": 1475000.00, "Taxable_Value": 1250000.00, "CGST": 112500.00, "SGST": 112500.00, "IGST": 0.00, "GSTR_3B_Filed": "YES", "ITC_Availability": "Available", "Reason_For_Ineligibility": "N/A"},
    {"Supplier_GSTIN": "07AAAAA1002A1Z5", "Trade_Name": "Apex Logistics India", "Invoice_No": "INV-LOG-441", "Invoice_Type": "Regular", "Invoice_Date": "12-04-2024", "Invoice_Value": 25000.00, "Taxable_Value": 25000.00, "CGST": 0.00, "SGST": 0.00, "IGST": 0.00, "GSTR_3B_Filed": "YES", "ITC_Availability": "Ineligible", "Reason_For_Ineligibility": "Paid in cash violating Sec 40A(3)"},
    {"Supplier_GSTIN": "07AAAAA1003A1Z5", "Trade_Name": "Legal Firm & Co India", "Invoice_No": "INV-LEG-881", "Invoice_Type": "Regular", "Invoice_Date": "15-04-2024", "Invoice_Value": 177000.00, "Taxable_Value": 150000.00, "CGST": 13500.00, "SGST": 13500.00, "IGST": 0.00, "GSTR_3B_Filed": "YES", "ITC_Availability": "Available", "Reason_For_Ineligibility": "N/A"},
    {"Supplier_GSTIN": "27AAACC5555K1Z2", "Trade_Name": "Commercial Premises Pvt Ltd", "Invoice_No": "INV-RENT-501", "Invoice_Type": "Regular", "Invoice_Date": "25-04-2024", "Invoice_Value": 413000.00, "Taxable_Value": 350000.00, "CGST": 31500.00, "SGST": 31500.00, "IGST": 0.00, "GSTR_3B_Filed": "YES", "ITC_Availability": "Available", "Reason_For_Ineligibility": "N/A"},
]

df_gstr2b = pd.DataFrame(gstr2b_data)
df_gstr2b.to_csv(CA_PACKAGE_DIR / "GSTR_2B_Reconciliation_FY2024-25.csv", index=False)
df_gstr2b.to_excel(CA_PACKAGE_DIR / "GSTR_2B_Reconciliation_FY2024-25.xlsx", index=False)

# ==============================================================================
# 4. OFFICIAL INCOME TAX e-FILING PORTAL AIS / FORM 26AS DATA (JSON & CSV)
# ==============================================================================
ais_json_payload = {
    "assessee_details": {
        "pan": "AAACA1234F",
        "assessee_name": "APEX GLOBAL CORP INDIA PRIVATE LIMITED",
        "financial_year": "2024-25",
        "assessment_year": "2025-26"
    },
    "part_a_tds_tcs_summary": [
        {
            "tan": "DELV00192A",
            "deductor_name": "Vanguard Trading India Pvt Ltd",
            "section": "194C",
            "amount_credited_inr": 13500000.0,
            "total_tds_deducted_inr": 270000.0,
            "total_tds_deposited_inr": 270000.0
        },
        {
            "tan": "MUMH00241B",
            "deductor_name": "HDFC Bank Limited",
            "section": "194A",
            "amount_credited_inr": 850000.0,
            "total_tds_deducted_inr": 85000.0,
            "total_tds_deposited_inr": 85000.0
        },
        {
            "tan": "DELA00331C",
            "deductor_name": "Apex Global Corp India Pvt Ltd",
            "section": "194J",
            "amount_credited_inr": 1200000.0,
            "total_tds_deducted_inr": 120000.0,
            "total_tds_deposited_inr": 120000.0
        }
    ],
    "part_b_sft_high_value_transactions": [
        {
            "sft_code": "SFT-005",
            "sft_description": "Purchase of Time Deposits (Fixed Deposit)",
            "reporting_entity": "HDFC Bank Ltd",
            "transaction_date": "2024-05-15",
            "reported_amount_inr": 850000.0,
            "book_status": "UNREPORTED_IN_BOOKS (Sec 68 Risk)"
        },
        {
            "sft_code": "SFT-014",
            "sft_description": "Sale of Listed Securities / Shares",
            "reporting_entity": "National Stock Exchange India Ltd",
            "transaction_date": "2024-08-20",
            "reported_amount_inr": 4500000.0,
            "book_status": "PARTIAL_MISMATCH"
        }
    ]
}

with open(CA_PACKAGE_DIR / "IncomeTax_AIS_Form26AS_FY2024-25.json", "w", encoding="utf-8") as f:
    json.dump(ais_json_payload, f, indent=2)

ais_csv_rows = [
    {"PAN": "AAACA1234F", "Section_SFT": "TDS-194C", "Description": "Contractor Payment", "Reporter": "Vanguard Trading India Pvt Ltd", "Reported_Amount": 13500000.0, "TDS_Deposited": 270000.0},
    {"PAN": "AAACA1234F", "Section_SFT": "SFT-005", "Description": "Fixed Deposit Interest", "Reporter": "HDFC Bank Ltd", "Reported_Amount": 850000.0, "TDS_Deposited": 85000.0},
    {"PAN": "AAACA1234F", "Section_SFT": "TDS-194J", "Description": "Professional Fees", "Reporter": "Apex Global Corp India Pvt Ltd", "Reported_Amount": 1200000.0, "TDS_Deposited": 120000.0},
    {"PAN": "AAACA1234F", "Section_SFT": "SFT-014", "Description": "Securities Transactions", "Reporter": "National Stock Exchange India", "Reported_Amount": 4500000.0, "TDS_Deposited": 0.0},
]
pd.DataFrame(ais_csv_rows).to_csv(CA_PACKAGE_DIR / "IncomeTax_AIS_Form26AS_FY2024-25.csv", index=False)

# ==============================================================================
# 5. REALISTIC FORMAL GST TAX INVOICES (PLAIN TEXT / PRINT LAYOUT)
# ==============================================================================
inv_1 = """====================================================================================================
                                      TAX INVOICE
====================================================================================================
Supplier: SHELL CORP INDIA PRIVATE LIMITED
Address: Plot 45, Okhla Industrial Area Phase-III, New Delhi - 110020
GSTIN: 27AAACS1001A1Z1 | PAN: AAACS1001A | State Code: 07 (Delhi)

Invoice No: INV-2024-1088                                Date of Invoice: 01-04-2024
Reverse Charge: NO                                       E-Way Bill No: 771122334455
Vehicle No: DL-01-AB-1234                                Transport Mode: Road

Billed To Customer:
VANGUARD TRADING INDIA PRIVATE LIMITED
Address: Plot 12, Cyber City Phase-II, Gurugram, Haryana - 122002
GSTIN: 27AAACV1234F1Z1 | State Code: 06 (Haryana)

----------------------------------------------------------------------------------------------------
S.No | HSN/SAC | Item Description                 | Qty  | Unit Rate (INR) | Taxable Value (INR)
----------------------------------------------------------------------------------------------------
 1.  | 8471    | Industrial Processing Equipment   |  1   | 1,35,00,000.00  |   1,35,00,000.00
----------------------------------------------------------------------------------------------------
                                                    Sub-Total Taxable Value: ₹1,35,00,000.00
                                                    CGST @ 9.0%:             ₹12,15,000.00
                                                    SGST @ 9.0%:             ₹12,15,000.00
                                                    TOTAL INVOICE VALUE:     ₹1,59,30,000.00
----------------------------------------------------------------------------------------------------
Amount in Words: One Crore Fifty-Nine Lakhs Thirty Thousand Indian Rupees Only.
Bank Details: State Bank of India A/C: 33009988112 | IFSC: SBIN0001004

Terms: Subject to Delhi Jurisdiction. Input Tax Credit Subject to CGST Sec 16(2) Physical Supply.
For SHELL CORP INDIA PRIVATE LIMITED
[Authorised Signatory]
===================================================================================================="""

with open(CA_PACKAGE_DIR / "GST_Tax_Invoice_INV-2024-1088.txt", "w", encoding="utf-8") as f:
    f.write(inv_1)

# ==============================================================================
# 6. FORM 3CD TAX AUDIT CLAUSE ANNEXURE (EXACT FORM 3CD TEMPLATE)
# ==============================================================================
f3cd_clause_21b = [
    {"Clause": "Clause 21(b)", "Sub_Clause": "Sec 40A(3)", "Voucher_Ref": "PAY-005", "Date": "12-04-2024", "Payee_Name": "Apex Logistics India", "Amount_INR": 25000.00, "Mode_of_Payment": "Hand Cash", "Rule_6DD_Exemption": "NONE", "Disallowance_Status": "100% DISALLOWED U/S 40A(3)"},
]

f3cd_clause_31a = [
    {"Clause": "Clause 31(a)", "Sub_Clause": "Sec 269SS", "Voucher_Ref": "REC-002", "Date": "05-04-2024", "Payer_Name": "Ramesh Kumar (Director)", "Amount_INR": 45000.00, "Mode_of_Acceptance": "Hand Cash Loan", "Penalty_Sec": "Sec 271D (100% Penalty)", "Reporting_Status": "REPORTABLE IN FORM 3CD CLAUSE 31(a)"},
]

with pd.ExcelWriter(CA_PACKAGE_DIR / "Form_3CD_Tax_Audit_Annexures_FY2024-25.xlsx") as writer:
    pd.DataFrame(f3cd_clause_21b).to_excel(writer, sheet_name="Clause 21b Cash Sec 40A(3)", index=False)
    pd.DataFrame(f3cd_clause_31a).to_excel(writer, sheet_name="Clause 31a Loans Sec 269SS", index=False)

print("Hyper-realistic CA Audit Data Bundle generated successfully!")
