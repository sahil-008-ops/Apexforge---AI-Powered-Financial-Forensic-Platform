"""
ApexForge Streamlit Investigation Platform
Interactive Forensic Auditing & Transaction-Tracing Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
from pathlib import Path
from typing import List, Dict, Any

from apexforge.models.data_models import (
    NormalizedDocument,
    DocumentType,
    Entity,
    Relationship,
    Transaction,
    TransactionCycle,
    AnomalyFinding,
    PolicyFinding,
)
from apexforge.ingestion.document_loader import DocumentLoader
from apexforge.generator.synthetic_data import SyntheticDataGenerator
from apexforge.agents.orchestrator import ForensicOrchestrator
from apexforge.graph.graph_store import TransactionGraphStore
from apexforge.rag.policy_store import RAGPolicyStore


st.set_page_config(
    page_title="ApexForge — Forensic Transaction Tracing Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for dark-themed forensic UI aesthetics
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.3rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #888888;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #1E222A;
        border-radius: 8px;
        padding: 15px;
        border-left: 4px solid #1E88E5;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .badge-critical {
        background-color: #D32F2F;
        color: white;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .badge-high {
        background-color: #F57C00;
        color: white;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .badge-medium {
        background-color: #FBC02D;
        color: black;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .badge-low {
        background-color: #388E3C;
        color: white;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_orchestrator():
    return ForensicOrchestrator()


def initialize_session():
    if "results" not in st.session_state:
        # Auto-run 50-document synthetic benchmark on startup
        gen = SyntheticDataGenerator(seed=42)
        docs = gen.generate_benchmark_dataset()
        orch = get_orchestrator()
        st.session_state["results"] = orch.run_investigation_pipeline(docs)


initialize_session()

# Sidebar Control Panel
st.sidebar.image("https://img.icons8.com/color/96/000000/shield-with-authorization.png", width=64)
st.sidebar.title("ApexForge Platform")
st.sidebar.caption("AI-Powered Forensic Tracing Engine v1.0")

st.sidebar.markdown("---")
st.sidebar.subheader("Benchmark Datasets")
if st.sidebar.button("🚀 Load 50-Doc Fraud Benchmark", use_container_width=True):
    with st.spinner("Processing 50 synthetic forensic documents across multi-agent pipeline..."):
        gen = SyntheticDataGenerator(seed=42)
        docs = gen.generate_benchmark_dataset()
        orch = get_orchestrator()
        st.session_state["results"] = orch.run_investigation_pipeline(docs)
    st.sidebar.success("Benchmark Investigation Completed!")

st.sidebar.markdown("---")
st.sidebar.subheader("Pipeline Settings")
show_evidence_snippets = st.sidebar.checkbox("Show Raw Document Evidence", value=True)
min_cycle_length = st.sidebar.slider("Min Cycle Length", 2, 5, 2)
max_cycle_length = st.sidebar.slider("Max Cycle Length", 3, 8, 6)

results = st.session_state["results"]
docs: List[NormalizedDocument] = results["documents"]
entities: List[Entity] = results["entities"]
transactions: List[Transaction] = results["transactions"]
graph_store: TransactionGraphStore = results["graph_store"]
cycles: List[TransactionCycle] = results["cycles"]
anomalies: List[AnomalyFinding] = results["anomalies"]
policy_findings: List[PolicyFinding] = results["policy_findings"]
narrative = results["narrative"]
ledger = results["ledger"]

# Header
st.markdown('<div class="main-header">🛡️ APEXFORGE</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered Forensic Financial Auditing & Transaction Tracing Platform</div>', unsafe_allow_html=True)

# Navigation Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Executive Summary",
    "📁 Document Ingestion",
    "🕸️ Transaction Graph",
    "🔄 Cycles & Anomalies",
    "📜 Policy RAG Verification",
    "🔐 Audit Ledger & Report",
])

# ==============================================================================
# TAB 1: EXECUTIVE SUMMARY
# ==============================================================================
with tab1:
    st.header("Executive Investigation Overview")
    
    # KPI Metrics
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    total_vol = sum(t.amount for t in transactions)
    crit_count = sum(1 for a in anomalies if a.severity.value == "CRITICAL")
    
    col1.metric("Ingested Docs", len(docs))
    col2.metric("Extracted Entities", len(entities))
    col3.metric("Transactions", len(transactions))
    col4.metric("Total Volume ($)", f"${total_vol:,.0f}")
    col5.metric("Circular Loops", len(cycles), delta=f"{len(cycles)} loops", delta_color="inverse")
    col6.metric("Critical Anomalies", crit_count, delta=f"{crit_count} Critical", delta_color="inverse")
    
    st.markdown("---")
    
    st.subheader("🤖 Executive Narrative Summary")
    st.info(narrative.executive_summary)
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("### 📌 Key Observed Facts")
        for fact in narrative.observed_facts[:6]:
            st.markdown(f"- {fact}")
            
        st.markdown("### 🔍 Forensic Hypotheses")
        for hyp in narrative.hypotheses:
            st.warning(hyp)

    with col_right:
        st.markdown("### 🚨 Detected Anomaly Distribution")
        anomaly_types = {}
        for a in anomalies:
            anomaly_types[a.anomaly_type.value] = anomaly_types.get(a.anomaly_type.value, 0) + 1
        
        df_types = pd.DataFrame(list(anomaly_types.items()), columns=["Anomaly Category", "Count"])
        fig_pie = px.pie(df_types, names="Anomaly Category", values="Count", hole=0.4, title="Anomalies by Category")
        st.plotly_chart(fig_pie, use_container_width=True)

# ==============================================================================
# TAB 2: DOCUMENT INGESTION
# ==============================================================================
with tab2:
    st.header("Document Ingestion & SHA3-256 Provenance Ledger")
    
    # Upload new file widget
    uploaded_files = st.file_uploader(
        "Ingest Financial Evidence Files (PDF, CSV, TXT, EML)",
        type=["pdf", "csv", "txt", "eml"],
        accept_multiple_files=True
    )
    if uploaded_files:
        loader = DocumentLoader()
        new_docs = []
        for uf in uploaded_files:
            content = uf.read()
            doc = loader.load_document(uf.name, override_text=content.decode("utf-8", errors="ignore"))
            new_docs.append(doc)
        
        if st.button("Process Ingested Files"):
            with st.spinner("Executing extraction on new documents..."):
                all_docs = docs + new_docs
                st.session_state["results"] = get_orchestrator().run_investigation_pipeline(all_docs)
                st.rerun()

    st.markdown("### Ingested Evidence Documents")
    
    doc_table_data = []
    for d in docs:
        doc_table_data.append({
            "Document ID": d.document_id,
            "Filename": d.filename,
            "Type": d.document_type.value.upper(),
            "SHA3-256 Hash": d.sha3_256_hash[:24] + "...",
            "Status": d.processing_status.value,
            "Ingested Timestamp": d.ingestion_timestamp[:19],
        })
    st.dataframe(pd.DataFrame(doc_table_data), use_container_width=True)
    
    st.markdown("### Document Content & Evidence Viewer")
    selected_doc_id = st.selectbox("Select Document ID to View", [d.document_id for d in docs])
    target_doc = next((d for d in docs if d.document_id == selected_doc_id), None)
    if target_doc:
        st.text_area("Extracted Raw Content", target_doc.extracted_text, height=250)
        st.json(target_doc.metadata)

# ==============================================================================
# TAB 3: TRANSACTION GRAPH EXPLORER
# ==============================================================================
with tab3:
    st.header("Transaction Graph & Entity Relationship Explorer")
    
    # Render interactive network graph using Plotly
    g = graph_store.graph
    pos = nx.spring_layout(g, seed=42)
    
    edge_x = []
    edge_y = []
    for edge in g.edges():
        if edge[0] in pos and edge[1] in pos:
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#555555'),
        hoverinfo='none',
        mode='lines'
    )

    node_x = []
    node_y = []
    node_text = []
    node_color = []
    
    for node in g.nodes():
        if node in pos:
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            lbl = g.nodes[node].get("label", node)
            ntype = g.nodes[node].get("node_type", "Unknown")
            node_text.append(f"Label: {lbl}<br>ID: {node}<br>Type: {ntype}")
            
            if ntype == "Company":
                node_color.append("#1E88E5")
            elif ntype == "Account":
                node_color.append("#D32F2F")
            elif ntype == "Person":
                node_color.append("#388E3C")
            elif ntype == "Invoice":
                node_color.append("#FBC02D")
            else:
                node_color.append("#888888")

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        textposition="top center",
        text=[g.nodes[n].get("label", n) for n in g.nodes() if n in pos],
        hovertext=node_text,
        marker=dict(
            showscale=False,
            color=node_color,
            size=18,
            line_width=2
        )
    )

    fig_net = go.Figure(data=[edge_trace, node_trace],
                 layout=go.Layout(
                    title='Unified Entity-Transaction Graph',
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    paper_bgcolor='#0E1117',
                    plot_bgcolor='#0E1117',
                 ))
    
    st.plotly_chart(fig_net, use_container_width=True)
    
    # Path Tracing Tool
    st.subheader("🔎 Entity Path Tracing Tool")
    col_a, col_b = st.columns(2)
    all_ent_ids = [e.entity_id for e in entities]
    if len(all_ent_ids) >= 2:
        src_id = col_a.selectbox("Source Entity", all_ent_ids, index=0)
        tgt_id = col_b.selectbox("Target Entity", all_ent_ids, index=min(1, len(all_ent_ids)-1))
        
        if st.button("Find Payment & Relationship Paths"):
            paths = graph_store.trace_transaction_path(src_id, tgt_id)
            if paths:
                st.success(f"Found {len(paths)} simple path(s) between entities:")
                for p in paths:
                    st.code(" -> ".join(p))
            else:
                st.warning("No direct path found within 6 hops.")

# ==============================================================================
# TAB 4: CYCLES & ANOMALY ENGINE
# ==============================================================================
with tab4:
    st.header("Graph Cycle Detection & 12-Category Anomaly Engine")
    
    st.subheader("🔄 Detected Circular Transaction Loops")
    if cycles:
        cycle_table = []
        for c in cycles:
            cycle_table.append({
                "Cycle ID": c.cycle_id,
                "Cycle Path": " ➔ ".join([e.split(" ")[0] for e in c.entities_involved]),
                "Total Amount": f"${c.total_amount:,.2f}",
                "Hop Length": c.cycle_length,
                "Risk Classification": c.risk_level,
                "Source Docs": ", ".join(c.source_documents),
            })
        st.dataframe(pd.DataFrame(cycle_table), use_container_width=True)
    else:
        st.info("No closed transaction cycles detected in graph.")

    st.markdown("---")
    st.subheader("🚨 Explainable Anomaly Findings Table")
    
    anomaly_data = []
    for a in anomalies:
        anomaly_data.append({
            "Anomaly ID": a.anomaly_id,
            "Category": a.anomaly_type.value,
            "Severity": a.severity.value,
            "Explainable Score": f"{a.anomaly_score:.2f}",
            "Explanation & Feature Basis": a.explanation,
            "Evidence Docs": ", ".join(a.evidence_documents),
        })
    
    st.dataframe(pd.DataFrame(anomaly_data), use_container_width=True)

# ==============================================================================
# TAB 5: POLICY RAG VERIFICATION
# ==============================================================================
with tab5:
    st.header("RAG Policy Verification & Compliance Engine")
    
    # Vector Search query tool
    st.subheader("🔍 Query Internal Policy Vector Database (ChromaDB)")
    policy_query = st.text_input("Enter natural language policy query:", "smurfing CTR threshold structuring invoice approval segregation of duties")
    
    if policy_query:
        p_store = get_orchestrator().policy_store
        retrieved = p_store.search_policies(policy_query, top_k=3)
        
        for idx, res in enumerate(retrieved):
            with st.expander(f"📌 [{res['relevance_score']:.2f} Relevance] {res['title']} ({res['section']})"):
                st.markdown(f"**Citation:** `{res['citation']}`")
                st.write(res["text"])

    st.markdown("---")
    st.subheader("📋 Matched Policy Control Violations")
    policy_table = []
    for pf in policy_findings:
        policy_table.append({
            "Finding ID": pf.finding_id,
            "Policy Title": pf.policy_title,
            "Section": pf.policy_section,
            "Violation Type": pf.violation_type,
            "Citation": pf.citation,
        })
    st.dataframe(pd.DataFrame(policy_table), use_container_width=True)

# ==============================================================================
# TAB 6: AUDIT LEDGER & REPORT
# ==============================================================================
with tab6:
    st.header("Forensic Audit Ledger & Report")
    
    col_l1, col_l2 = st.columns([2, 1])
    
    with col_l1:
        st.subheader("🔐 SHA3-256 Tamper-Evident Audit Ledger")
        
        is_valid, count, tampered_idx, msg = ledger.verify_chain_integrity()
        if is_valid:
            st.success(f"✅ LEDGER INTEGRITY VERIFIED: {msg}")
        else:
            st.error(f"❌ TAMPER DETECTED: {msg}")

        ledger_entries = ledger.export_ledger_dict()
        st.dataframe(pd.DataFrame(ledger_entries), use_container_width=True)

    with col_l2:
        st.subheader("🧪 Tamper Demonstration")
        st.caption("Test the cryptographic hash chain by modifying a historic entry.")
        if st.button("⚠️ Simulate Data Tampering", use_container_width=True):
            if ledger.chain:
                ledger.chain[0].finding = "[TAMPERED BY ATTACKER] Altered historic transaction amount."
                st.warning("Tampered entry #0 payload! Re-verifying ledger integrity...")
                st.rerun()

        if st.button("🔄 Reset Ledger", use_container_width=True):
            st.session_state["results"] = get_orchestrator().run_investigation_pipeline(docs)
            st.rerun()

    st.markdown("---")
    st.subheader("📄 Full Forensic Investigation Report")
    
    report_text = f"""# FORENSIC AUDIT INVESTIGATION REPORT
**Generated by ApexForge Platform**
**Date:** 2026-03-26

## EXECUTIVE SUMMARY
{narrative.executive_summary}

## OBSERVED FACTS
""" + "\n".join([f"- {f}" for f in narrative.observed_facts]) + """

## FORENSIC HYPOTHESES & CIRCULAR PAYMENT FLOWS
""" + "\n".join([f"- {h}" for h in narrative.hypotheses]) + """

## POLICY & CONTROL VIOLATIONS
""" + "\n".join([f"- {pv}" for pv in narrative.policy_violations]) + """

## UNRESOLVED QUESTIONS
""" + "\n".join([f"- {uq}" for uq in narrative.unresolved_questions])

    st.download_button(
        label="📥 Download Official Forensic Report (.MD)",
        data=report_text,
        file_name="ApexForge_Forensic_Investigation_Report.md",
        mime="text/markdown",
    )
