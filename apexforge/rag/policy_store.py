"""
Section 8: RAG Policy Library & Verification Vector Store
Indexes internal financial policies, procurement controls, segregation-of-duties rules,
and audit case precedents into ChromaDB (with TF-IDF / vector fallback) to evaluate compliance.
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
        """Default internal financial policies and forensic control standards."""
        self.policies = [
            {
                "id": "POL-CTR-001",
                "title": "Currency Transaction & Anti-Smurfing Threshold Policy",
                "section": "Section 4.1 — Mandatory CTR Reporting",
                "content": (
                    "All single or aggregated financial transactions exceeding $10,000.00 USD within a 24-hour period "
                    "must be reported via Currency Transaction Reports (CTR). Intentionally structuring, splitting, "
                    "or breaking up payments into multiple transfers under $10,000.00 to avoid regulatory reporting (smurfing) "
                    "is strictly prohibited under Policy FIN-401 and Federal AML regulations."
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
                    "Approval must be granted by an independent authorized signatory with appropriate financial threshold limits."
                ),
                "category": "Internal Audit",
            },
            {
                "id": "POL-PROC-003",
                "title": "Corporate Procurement & Vendor Verification Policy",
                "section": "Section 6.2 — Backing Documentation Requirements",
                "content": (
                    "All corporate disbursements exceeding $5,000.00 USD must be backed by a verified Purchase Order (PO), "
                    "an itemized Vendor Invoice, and written proof of receipt/deliverable verification. Payments made to "
                    "unverified counterparties or shell entities lacking a physical business address are strictly prohibited."
                ),
                "category": "Procurement Controls",
            },
            {
                "id": "POL-CIRC-004",
                "title": "Related Party Transactions & Circular Financing Prohibition",
                "section": "Section 8.4 — Circular Cash Flow Prevention",
                "content": (
                    "Circular money movements where funds are transferred through intermediary shell entities, subsidiaries, "
                    "or offshore accounts only to return to the originating entity cluster are classified as high-risk anomalous loops. "
                    "Any circular transaction pattern lacking clear commercial substance must be immediately frozen and audited."
                ),
                "category": "Financial Crime Prevention",
            },
            {
                "id": "CASE-PREC-101",
                "title": "Forensic Precedent — State v. Vanguard Shell Network (2024)",
                "section": "Precedent Case #2024-889",
                "content": (
                    "In State v. Vanguard, defendants utilized 3 layer shell companies to transfer $1.2M in round-trip wire payments. "
                    "The court established that identical dollar amounts flowing in a closed loop across related accounts within 48 hours "
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
