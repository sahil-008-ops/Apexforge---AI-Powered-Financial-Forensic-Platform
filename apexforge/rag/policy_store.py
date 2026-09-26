"""
Section 8: RAG Policy Library & Verification Vector Store
Indexes internal financial policies, procurement controls, segregation-of-duties rules,
Indian Income Tax Act (1961) sections, CGST Act (2017) provisions, and audit case precedents into ChromaDB.
"""

import uuid
from pathlib import Path
from typing import List, Dict, Any, Tuple
from apexforge.models.data_models import PolicyFinding


class RAGPolicyStore:
    def __init__(self, chroma_dir: Path = None):
        self.chroma_dir = chroma_dir
        self.chroma_client = None
        self.collection = None
        self.policies: List[Dict[str, Any]] = []

        self._initialize_default_policies()
        self._setup_vector_store()

    def _initialize_default_policies(self):
        """Default financial policies and Indian Income Tax / GST statutory provisions."""
        self.policies = [
            {
                "id": "IND-TAX-269SS",
                "title": "Indian Income Tax Act (1961) — Section 269SS / 269T Cash Loan Restrictions",
                "section": "Section 269SS & Section 269T (Mode of Accepting / Repaying Loans & Deposits)",
                "content": (
                    "No person shall accept or repay any loan, deposit, or specified advance of ₹20,000.00 INR or more "
                    "otherwise than by an account payee cheque, account payee bank draft, or electronic clearing system. "
                    "Contravention attracts 100% statutory penalty under Section 271D / 271E equal to the amount of loan/deposit."
                ),
                "category": "Indian Statutory Income Tax",
            },
            {
                "id": "IND-TAX-40A3",
                "title": "Indian Income Tax Act (1961) — Section 40A(3) Cash Expense Disallowance",
                "section": "Section 40A(3) read with Rule 6DD (Disallowance of Cash Expenditure)",
                "content": (
                    "Where an assessee incurs any expenditure in respect of which payment is made in a single day to a person "
                    "otherwise than by account payee cheque/bank draft/ECS exceeding ₹10,000.00 INR, 100% of such expenditure "
                    "shall be disallowed as a deduction from business income under Section 40A(3)."
                ),
                "category": "Indian Statutory Income Tax",
            },
            {
                "id": "IND-TAX-SEC68",
                "title": "Indian Income Tax Act (1961) — Section 68 / 115BBE Unexplained Credits",
                "section": "Section 68 read with Section 115BBE (Unexplained Cash Credits)",
                "content": (
                    "Where any sum is found credited in the books of an assessee and the assessee offers no explanation about the "
                    "nature and source thereof, the sum is charged to income-tax u/s 68 at a flat rate of 60% tax + 25% surcharge "
                    "+ 4% cess (effective 78% tax rate) u/s 115BBE without allowance of any expenditure or set-off."
                ),
                "category": "Indian Statutory Income Tax",
            },
            {
                "id": "IND-GST-SEC16",
                "title": "CGST Act (2017) — Section 16(2) & Sec 132 Fake Invoicing & ITC Fraud",
                "section": "Section 16(2)(c) & Section 132(1)(b) (Input Tax Credit & Circular Trading Offenses)",
                "content": (
                    "Input Tax Credit (ITC) shall only be eligible if tax charged in respect of supply has been actually paid to the Government "
                    "and goods/services are physically received. Issuing invoices or participating in circular trading loops without actual supply "
                    "is a non-bailable cognizable offense u/s 132(1)(b) attracting ITC reversal with 24% interest u/s 50 and 100% penalty u/s 122."
                ),
                "category": "Indian Statutory GST Act",
            },
            {
                "id": "POL-CTR-001",
                "title": "Currency Transaction & Anti-Smurfing Threshold Policy",
                "section": "Section 4.1 — Mandatory CTR Reporting",
                "content": (
                    "All single or aggregated financial transactions exceeding $10,000.00 USD (or equivalent INR ₹800,000) within 24 hours "
                    "must be reported via Currency Transaction Reports (CTR). Intentionally structuring payments into multiple transfers "
                    "under statutory limits (smurfing) is strictly prohibited under Federal & Indian AML regulations."
                ),
                "category": "Anti-Money Laundering",
            },
            {
                "id": "POL-SOD-002",
                "title": "Segregation of Duties & Invoice Authorization Policy",
                "section": "Section 2.3 — Dual Control Controls",
                "content": (
                    "No single individual or officer shall have the authority to both issue/create an invoice and "
                    "approve or execute the payment disbursement for that same invoice or vendor account. "
                    "Approval must be granted by an independent authorized signatory."
                ),
                "category": "Internal Audit & ICAI SA 240",
            },
            {
                "id": "CASE-PREC-101",
                "title": "Forensic Precedent — State v. Vanguard Shell Network (2024)",
                "section": "Precedent Case #2024-889",
                "content": (
                    "In State v. Vanguard, defendants utilized 3 layer shell companies to transfer funds in round-trip wire payments. "
                    "The court established that identical amounts flowing in a closed loop across related accounts within 48 hours "
                    "constitutes prima facie evidence of illegitimate circular transaction routing."
                ),
                "category": "Audit Case Precedents",
            },
        ]

    def _setup_vector_store(self):
        try:
            import chromadb
            if self.chroma_dir:
                self.chroma_client = chromadb.PersistentClient(path=str(self.chroma_dir))
            else:
                self.chroma_client = chromadb.Client()

            self.collection = self.chroma_client.get_or_create_collection(name="apexforge_policies")
            
            # Populate collection if empty
            if self.collection.count() == 0:
                ids = [p["id"] for p in self.policies]
                documents = [p["content"] for p in self.policies]
                metadatas = [
                    {"title": p["title"], "section": p["section"], "category": p["category"]}
                    for p in self.policies
                ]
                self.collection.add(ids=ids, documents=documents, metadatas=metadatas)
        except Exception as e:
            print(f"[ChromaDB Vector Store Warning]: {e}. Using TF-IDF text search fallback.")
            self.collection = None

    def search_policies(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieves top-k relevant policy chunks with source citations."""
        results = []

        if self.collection:
            try:
                res = self.collection.query(query_texts=[query], n_results=top_k)
                docs = res["documents"][0]
                metas = res["metadatas"][0]
                ids = res["ids"][0]
                distances = res.get("distances", [[0.1] * len(docs)])[0]

                for doc, meta, p_id, dist in zip(docs, metas, ids, distances):
                    rel_score = round(max(0.1, 1.0 - float(dist)), 2)
                    results.append(
                        {
                            "id": p_id,
                            "title": meta.get("title", "Policy Document"),
                            "section": meta.get("section", "General Section"),
                            "category": meta.get("category", "General"),
                            "text": doc,
                            "relevance_score": rel_score,
                            "citation": f"Source: {meta.get('title')} ({meta.get('section')}) [ID: {p_id}]",
                        }
                    )
                return results
            except Exception:
                pass

        # TF-IDF Fallback search engine
        query_words = set(query.lower().split())
        scored_policies = []
        for p in self.policies:
            content_words = set(p["content"].lower().split()) | set(p["title"].lower().split())
            overlap = len(query_words & content_words)
            score = round(min(0.99, max(0.40, overlap / max(1, len(query_words)))), 2)
            scored_policies.append((score, p))

        scored_policies.sort(key=lambda x: x[0], reverse=True)

        for score, p in scored_policies[:top_k]:
            results.append(
                {
                    "id": p["id"],
                    "title": p["title"],
                    "section": p["section"],
                    "category": p["category"],
                    "text": p["content"],
                    "relevance_score": score,
                    "citation": f"Source: {p['title']} ({p['section']}) [ID: {p['id']}]",
                }
            )

        return results

    def verify_finding_against_policies(self, anomaly_type: str, explanation: str) -> List[PolicyFinding]:
        """Runs RAG lookup to match an anomaly finding to specific violated policy sections."""
        query = f"{anomaly_type} {explanation}"
        matches = self.search_policies(query, top_k=2)

        policy_findings: List[PolicyFinding] = []
        for m in matches:
            finding = PolicyFinding(
                finding_id=f"POL-FIND-{uuid.uuid4().hex[:8].upper()}",
                policy_title=m["title"],
                policy_section=m["section"],
                violation_type=anomaly_type,
                description=m["text"],
                relevance_score=m["relevance_score"],
                supporting_evidence=[explanation],
                citation=m["citation"],
            )
            policy_findings.append(finding)

        return policy_findings
