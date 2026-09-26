"""
Indian Income Tax Act (1961) & GST Act (2017) CA Audit Engine
Provides Chartered Accountant (CA) tax audit compliance checking, Form 3CD clause mappings,
GST Input Tax Credit (ITC) fraud analysis, and ICAI SA 240/250 compliant audit working paper generation.
"""

import uuid
from typing import List, Dict, Any
from apexforge.models.data_models import (
    Transaction,
    Entity,
    Relationship,
    TransactionCycle,
    AnomalyFinding,
    AnomalyCategory,
    AnomalySeverity,
)


class IndianCATaxAuditEngine:
    def __init__(self):
        # Statutory Thresholds under Indian Laws
        self.SEC_269SS_LIMIT = 20000.0  # Cash loan/deposit limit (Sec 269SS / 269T)
        self.SEC_40A3_LIMIT = 10000.0   # Cash payment disallowance limit per day u/s 40A(3)
        self.GST_180_DAYS_LIMIT = 180    # Section 16(2) GST ITC reversal window

    def evaluate_indian_tax_compliance(
        self,
        transactions: List[Transaction],
        entities: List[Entity],
        relationships: List[Relationship],
        cycles: List[TransactionCycle],
    ) -> Dict[str, Any]:
        tax_findings: List[Dict[str, Any]] = []
        form_3cd_clause_21b: List[Dict[str, Any]] = []  # Sec 40A(3) Cash Payments
        form_3cd_clause_31a: List[Dict[str, Any]] = []  # Sec 269SS Cash Loans Accepted
        form_3cd_clause_31b: List[Dict[str, Any]] = []  # Sec 269T Cash Loans Repaid
        gst_itc_risks: List[Dict[str, Any]] = []        # GST Circular Trading / Sec 16(2)

        for tx in transactions:
            amt = tx.amount
            payment_ref = tx.payment_reference.lower()
            ev_text = tx.evidence_text.lower()
            is_cash = any(k in payment_ref or k in ev_text for k in ["cash", "hand payment", "currency deposit", "tranche"])

            # 1. Income Tax Act Sec 269SS / 269T: Cash Loans/Deposits >= Rs. 20,000
            if is_cash and amt >= self.SEC_269SS_LIMIT:
                risk_item = {
                    "tx_id": tx.transaction_id,
                    "sender": tx.sender_name,
                    "receiver": tx.receiver_name,
                    "amount": amt,
                    "section": "Section 269SS / 269T (Income Tax Act, 1961)",
                    "penalty_provision": "Section 271D / 271E (100% penalty equivalent to transaction amount)",
                    "form_3cd_clause": "Clause 31(a) / 31(b)",
                    "severity": "CRITICAL",
                    "explanation": f"Cash transfer of ₹{amt:,.2f} between '{tx.sender_name}' and '{tx.receiver_name}' violates Section 269SS/269T limit of ₹20,000. Attracts 100% statutory penalty under Sec 271D/271E.",
                }
                tax_findings.append(risk_item)
                if "repay" in ev_text or "returned" in ev_text:
                    form_3cd_clause_31b.append(risk_item)
                else:
                    form_3cd_clause_31a.append(risk_item)

            # 2. Income Tax Act Sec 40A(3): Disallowance of Cash Expenditure > Rs. 10,000
            if is_cash and amt > self.SEC_40A3_LIMIT and "expense" in ev_text or "vendor" in ev_text or "invoice" in ev_text:
                disallowance_item = {
                    "tx_id": tx.transaction_id,
                    "payer": tx.sender_name,
                    "payee": tx.receiver_name,
                    "amount": amt,
                    "section": "Section 40A(3) (Income Tax Act, 1961)",
                    "form_3cd_clause": "Clause 21(b)",
                    "disallowance_percentage": "100% Disallowance from Business Income",
                    "severity": "HIGH",
                    "explanation": f"Cash expenditure of ₹{amt:,.2f} paid to '{tx.receiver_name}' exceeds daily statutory ceiling of ₹10,000 u/s 40A(3). Subject to 100% disallowance in Tax Audit Report.",
                }
                tax_findings.append(disallowance_item)
                form_3cd_clause_21b.append(disallowance_item)

            # 3. Income Tax Act Sec 68 / 69: Unexplained Cash Credits / Shell Accounts
            if "offshore" in tx.receiver_name.lower() or "shell" in tx.sender_name.lower():
                tax_findings.append({
                    "tx_id": tx.transaction_id,
                    "sender": tx.sender_name,
                    "receiver": tx.receiver_name,
                    "amount": amt,
                    "section": "Section 68 / 69 (Unexplained Cash Credits / Investments)",
                    "tax_rate_applicable": "Section 115BBE @ 78% (60% Tax + 25% Surcharge + 4% Cess)",
                    "form_3cd_clause": "General Tax Risk / SA 240 Fraud Consideration",
                    "severity": "CRITICAL",
                    "explanation": f"High-risk transfer of ₹{amt:,.2f} involving potential shell entity '{tx.sender_name}'. Subject to addition u/s 68/69 taxed @ 78% u/s 115BBE without deduction of any expenditure.",
                })

        # 4. GST Act 2017: Circular Trading & Fake Invoice ITC Claims u/s 16(2)(c) & Sec 132
        for cyc in cycles:
            gst_item = {
                "cycle_id": cyc.cycle_id,
                "involved_entities": cyc.entities_involved,
                "total_volume": cyc.total_amount,
                "section": "Section 16(2)(c) & Section 132(1)(b) (CGST Act, 2017)",
                "offense": "Fake Invoicing / Circular Trading without Actual Supply of Goods/Services",
                "severity": "CRITICAL",
                "audit_action": "Mandatory Input Tax Credit (ITC) Reversal with 24% Interest u/s 50 & 100% Penalty u/s 122",
                "explanation": f"Detected circular loop totaling ₹{cyc.total_amount:,.2f} across {cyc.cycle_length} parties. In GST audit, round-trip transactions without physical movement of goods constitute artificial turnover inflation & fraudulent ITC pass-through under CGST Sec 132.",
            }
            gst_itc_risks.append(gst_item)
            tax_findings.append(gst_item)

        # 5. CA Working Paper Summary Calculation
        tot_disallowance_40a3 = sum(i["amount"] for i in form_3cd_clause_21b)
        tot_269ss_penalty_risk = sum(i["amount"] for i in form_3cd_clause_31a) + sum(i["amount"] for i in form_3cd_clause_31b)
        tot_gst_itc_at_risk = sum(c["total_volume"] for c in gst_itc_risks)

        return {
            "all_tax_findings": tax_findings,
            "form_3cd_clause_21b": form_3cd_clause_21b,
            "form_3cd_clause_31a": form_3cd_clause_31a,
            "form_3cd_clause_31b": form_3cd_clause_31b,
            "gst_itc_risks": gst_itc_risks,
            "summary_metrics": {
                "total_sec_40a3_disallowance": tot_disallowance_40a3,
                "total_sec_269ss_penalty_exposure": tot_269ss_penalty_risk,
                "total_gst_circular_itc_at_risk": tot_gst_itc_at_risk,
                "total_flagged_tax_items": len(tax_findings),
            }
        }

    def generate_ca_working_paper_md(
        self, audit_data: Dict[str, Any], entity_name: str = "Client Assessee Ltd", ay: str = "2026-27"
    ) -> str:
        """Generates an ICAI SA 240 / SA 250 compliant Tax Audit Working Paper (W/P)."""
        metrics = audit_data["summary_metrics"]
        clause_21b = audit_data["form_3cd_clause_21b"]
        clause_31a = audit_data["form_3cd_clause_31a"]
        clause_31b = audit_data["form_3cd_clause_31b"]
        gst_risks = audit_data["gst_itc_risks"]

        md = f"""# CHARTERED ACCOUNTANT TAX AUDIT WORKING PAPER (W/P)
**Standard on Auditing (SA) 240 / SA 250 Compliance File**
**Client Name:** {entity_name}
**Assessment Year (AY):** {ay} | **Financial Year (FY):** 2025-26
**Audit Firm:** ApexForge CA Forensic & Statutory Tax Audit Practice

---

## 1. EXECUTIVE TAX RISK SUMMARY
- **Form 3CD Clause 21(b) Disallowances [Sec 40A(3)]:** ₹{metrics['total_sec_40a3_disallowance']:,.2f}
- **Form 3CD Clause 31(a)/31(b) Penalty Exposure [Sec 269SS/269T]:** ₹{metrics['total_sec_269ss_penalty_exposure']:,.2f}
- **GST Circular Trading / Bogus ITC at Risk [CGST Sec 16(2)/132]:** ₹{metrics['total_gst_circular_itc_at_risk']:,.2f}
- **Total Statutory Observations Flagged:** {metrics['total_flagged_tax_items']} items

---

## 2. FORM 3CD TAX AUDIT REPORT CLAUSE MAPPINGS

### A. Clause 21(b) — Disallowance u/s 40A(3) for Cash Payments > ₹10,000
*Ref: Income Tax Act, 1961 — Section 40A(3) read with Rule 6DD*
"""
        if clause_21b:
            for item in clause_21b:
                md += f"- **Tx ID:** `{item['tx_id']}` | **Payer:** {item['payer']} ➔ **Payee:** {item['payee']} | **Amount:** ₹{item['amount']:,.2f}\n  *Auditor Note:* {item['explanation']}\n"
        else:
            md += " *Nil observations under Clause 21(b).*\n"

        md += """
### B. Clause 31(a) & 31(b) — Particulars of Cash Loans / Deposits Accepted/Repaid >= ₹20,000
*Ref: Income Tax Act, 1961 — Section 269SS & Section 269T (Attracts 100% Penalty u/s 271D/271E)*
"""
        if clause_31a or clause_31b:
            for item in clause_31a + clause_31b:
                md += f"- **Tx ID:** `{item['tx_id']}` | **Sender:** {item['sender']} ➔ **Receiver:** {item['receiver']} | **Amount:** ₹{item['amount']:,.2f}\n  *Auditor Note:* {item['explanation']} (Penalty Provision: {item['penalty_provision']})\n"
        else:
            md += " *Nil observations under Clause 31(a)/31(b).*\n"

        md += """
---

## 3. GST ACT (2017) AUDIT FINDINGS & INPUT TAX CREDIT (ITC) FRAUD ANALYSIS

### A. Circular Trading & Fake Invoicing without Physical Delivery [CGST Sec 132(1)(b)]
"""
        if gst_risks:
            for g in gst_risks:
                md += f"- **Cycle ID:** `{g['cycle_id']}` | **Loop Volume:** ₹{g['total_volume']:,.2f}\n  *Parties Involved:* {' -> '.join(g['involved_entities'])}\n  *Audit Directive:* {g['audit_action']}\n"
        else:
            md += " *Nil circular trading risk detected under GST Laws.*\n"

        md += """
---

## 4. AUDITOR'S STATUTORY CONCLUSION & MANAGEMENT REPRESENTATION RECOMMENDATION
1. **Income Tax Returns (ITR-6):** Add back ₹""" + f"{metrics['total_sec_40a3_disallowance']:,.2f}" + """ to PGBP income under Section 40A(3).
2. **Management Representation Letter (MRL):** Obtain specific written representation from Directors regarding commercial expediency of cash transfers and confirmation of physical receipt of goods for all GST transactions.
3. **Form 3CD Auditor Qualification:** Include qualifying notes under Clause 21(b) and Clause 31(a)/(b) in the final Tax Audit Report signed u/s 44AB.
"""
        return md
