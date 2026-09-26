# 🛡️ APEXFORGE

## AI-Powered Forensic Transaction Tracing & Financial Investigation Platform

ApexForge is a production-style, multi-agent forensic financial auditing platform engineered to analyze heterogeneous financial evidence, trace transaction chains, detect circular payment loops, identify 12 categories of financial anomalies, verify findings against statutory policy libraries via RAG, and record tamper-evident audit logs using SHA3-256 hash chaining.

---

## 🌟 Key Architecture & Capabilities

1. **Document Ingestion Layer**:
   - Ingests PDF, CSV, TXT, Email (.eml), Images, and Chat logs with SHA3-256 document hashing for cryptographic provenance.
2. **Document Intelligence & Extraction**:
   - Extraction pipeline for Person, Organization, Bank, Account, Invoice, Transaction, Date, Amount, Currency, and Payment Reference entities.
   - Extracts relations (`OWNS`, `WORKS_FOR`, `PAID`, `RECEIVED`, `TRANSFERRED_TO`, `ISSUED`, `INVOICED`, `APPROVED`).
3. **Multi-Agent Orchestration**:
   - State-machine workflow coordinating 5 specialized agents:
     - Agent 1: Document / Extraction Agent
     - Agent 2: Linker / Pattern Agent
     - Agent 3: Anomaly Agent
     - Agent 4: Policy / Verification Agent
     - Agent 5: Reasoner Agent
4. **Transaction Graph & Circular Flow Detection**:
   - Dual-engine NetworkX & Neo4j graph storage layer.
   - Closed-loop cycle detection ($A \to B \to C \to A$) calculating cycle length, total amount, timestamps, and evidence sources.
5. **12-Category Anomaly Engine**:
   - Rule-based + statistical (Isolation Forest) evaluation covering structuring (smurfing), segregation of duties, duplicate transfers, unbacked payments, and high-value outliers.
6. **RAG Policy Library**:
   - Indexing of internal financial controls, procurement rules, and audit precedents into ChromaDB vector store with exact source citations.
7. **Forensic Audit Ledger**:
   - Cryptographic SHA3-256 hash-chained ledger ensuring tamper evidence across all agent findings.
8. **Interactive Streamlit Interface**:
   - 6-tab dashboard with interactive Plotly graph visualization, path tracing, anomaly tables, policy search, report downloader, and tamper simulation tool.

---

## 🚀 Quick Start Guide

### 1. Installation
```bash
git clone https://github.com/your-org/apexforge.git
cd apexforge
pip install -r requirements.txt
```

### 2. Run Test Suite
```bash
python -m pytest
```

### 3. Launch Streamlit Application
```bash
streamlit run app.py
```

---

## 🧪 Synthetic Benchmark
ApexForge comes pre-packaged with a 50-document reproducible synthetic fraud benchmark (seed=42) containing circular payment flows, smurfing patterns, and segregation-of-duties conflicts.
