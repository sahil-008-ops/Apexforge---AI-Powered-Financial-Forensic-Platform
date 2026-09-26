"""
ApexForge Streamlit Investigation Platform
Interactive Forensic Auditing & Transaction-Tracing Dashboard
Featuring All-Format Document Ingestion System, Non-Overlapping Interactive Graph Explorer,
and Indian Income Tax (1961) & GST Act (2017) Chartered Accountant Audit Engine.
"""

import os
import tempfile
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
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
from apexforge.ca_audit.ca_tax_engine import IndianCATaxAuditEngine


st.set_page_config(
    page_title="ApexForge — Forensic Tracing & CA Audit Platform",
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
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding-left: 14px;
        padding-right: 14px;
        border-radius: 4px;
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
st.sidebar.caption("AI Forensic & CA Tax Audit Engine v1.1")

st.sidebar.markdown("---")
st.sidebar.subheader("Benchmark Datasets")
if st.sidebar.button("🚀 Run 50-Doc Fraud Benchmark", use_container_width=True):
    with st.spinner("Executing multi-agent investigation across 50 benchmark documents..."):
        gen = SyntheticDataGenerator(seed=42)
        docs = gen.generate_benchmark_dataset()
        orch = get_orchestrator()
        st.session_state["results"] = orch.run_investigation_pipeline(docs)
    st.sidebar.success("Benchmark Investigation Completed!")

st.sidebar.markdown("---")
st.sidebar.subheader("Graph Visualization Engine")
graph_engine_choice = st.sidebar.radio(
    "Graph Rendering Engine",
    ["Interactive Pyvis Physics (Zero Overlap)", "Plotly Clean Spacing Matrix"],
    index=0
)

results = st.session_state["results"]
docs: List[NormalizedDocument] = results["documents"]
entities: List[Entity] = results["entities"]
transactions: List[Transaction] = results["transactions"]
graph_store: TransactionGraphStore = results["graph_store"]
cycles: List[TransactionCycle] = results["cycles"]
anomalies: List[AnomalyFinding] = results["anomalies"]
policy_findings: List[PolicyFinding] = results["policy_findings"]
ca_audit_results: Dict[str, Any] = results.get("ca_audit_results", {})
narrative = results["narrative"]
ledger = results["ledger"]

# Header
st.markdown('<div class="main-header">🛡️ APEXFORGE</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered Forensic Financial Auditing, Transaction Tracing & CA Tax Compliance Platform</div>', unsafe_allow_html=True)

# Navigation Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Executive Summary",
    "📁 Multi-File Ingestion",
    "🕸️ Clean Transaction Graph",
    "🔄 Cycles & Anomalies",
    "🇮🇳 CA Tax Audit (Income Tax & GST)",
    "📜 Policy RAG Verification",
    "🔐 Audit Ledger & Report",
])

# ==============================================================================
# TAB 1: EXECUTIVE SUMMARY
# ==============================================================================
with tab1:
    st.header("Executive Investigation Overview")
    
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
# TAB 2: MULTI-FILE INGESTION SYSTEM (ALL FILE TYPES SUPPORTED)
# ==============================================================================
with tab2:
    st.header("Universal Document Ingestion System")
    st.caption("Upload financial evidence files of ANY format (.PDF, .CSV, .XLSX, .DOCX, .TXT, .EML, .JSON, Images, .LOG, etc.)")
    
    uploaded_files = st.file_uploader(
        "Upload Financial Evidence Files (Any File Extension Supported)",
        type=None,
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if st.button("📥 Ingest & Process All Uploaded Documents", type="primary", use_container_width=True):
            loader = DocumentLoader()
            new_docs = []
            for uf in uploaded_files:
                raw_b = uf.read()
                doc = loader.load_document(
                    filepath=uf.name,
                    override_bytes=raw_b
                )
                new_docs.append(doc)
            
            with st.spinner(f"Ingesting {len(new_docs)} files across multi-agent pipeline..."):
                all_docs = docs + new_docs
                orch = get_orchestrator()
                st.session_state["results"] = orch.run_investigation_pipeline(all_docs)
                st.success(f"Successfully processed and ingested {len(new_docs)} new files!")
                st.rerun()

    st.markdown("---")
    st.subheader("Ingested Evidence Library & SHA3-256 Provenance")
    
    doc_table_data = []
    for d in docs:
        doc_table_data.append({
            "Document ID": d.document_id,
            "Filename": d.filename,
            "Type": d.document_type.value.upper(),
            "SHA3-256 Provenance Hash": d.sha3_256_hash,
            "Processing Status": d.processing_status.value.upper(),
            "Ingested Timestamp": d.ingestion_timestamp[:19],
        })
    st.dataframe(pd.DataFrame(doc_table_data), use_container_width=True)
    
    st.markdown("---")
    st.subheader("🔍 Document Raw Text & Metadata Inspector")
    selected_doc_id = st.selectbox("Select Document ID to View Extracted Content", [d.document_id for d in docs])
    target_doc = next((d for d in docs if d.document_id == selected_doc_id), None)
    if target_doc:
        c1, c2 = st.columns([3, 1])
        with c1:
            st.text_area("Extracted Plain Text", target_doc.extracted_text, height=300)
        with c2:
            st.markdown("**File Metadata**")
            st.json(target_doc.metadata)

# ==============================================================================
# TAB 3: CLEAN TRANSACTION GRAPH EXPLORER (NON-OVERLAPPING)
# ==============================================================================
with tab3:
    st.header("Clean Entity-Transaction Network Graph")
    st.caption("Visualizes relationships and payment routing with zero node overlap using force-directed physics layout.")

    st.markdown("#### ⚙️ Graph Filtering & Layout Controls")
    fc1, fc2, fc3 = st.columns(3)
    
    with fc1:
        allowed_types = st.multiselect(
            "Filter Node Types",
            ["Company", "Account", "Person", "Invoice", "Transaction", "Document"],
            default=["Company", "Account", "Person", "Invoice"]
        )
    with fc2:
        min_tx_val = st.slider("Min Transaction Value ($)", 0, 100000, 0, step=5000)
    with fc3:
        node_spacing = st.slider("Force Separation Distance", 1, 10, 5)

    g_raw = graph_store.graph
    sub_nodes = []
    for n, data in g_raw.nodes(data=True):
        ntype = data.get("node_type", "Unknown")
        if allowed_types and ntype not in allowed_types:
            continue
        sub_nodes.append(n)

    g_sub = g_raw.subgraph(sub_nodes).copy()

    if min_tx_val > 0:
        remove_edges = []
        for u, v, d in g_sub.edges(data=True):
            amt = d.get("amount", 0.0)
            if amt > 0 and amt < min_tx_val:
                remove_edges.append((u, v))
        g_sub.remove_edges_from(remove_edges)

    if "Pyvis" in graph_engine_choice:
        try:
            from pyvis.network import Network

            net = Network(height="650px", width="100%", bgcolor="#0E1117", font_color="white", directed=True)
            physics_config = {
                "physics": {
                    "barnesHut": {
                        "gravitationalConstant": -15000 * (node_spacing / 5.0),
                        "centralGravity": 0.1,
                        "springLength": 180 * (node_spacing / 5.0),
                        "springConstant": 0.03,
                        "damping": 0.09,
                        "avoidOverlap": 1.0
                    },
                    "maxVelocity": 50,
                    "minVelocity": 0.1,
                    "solver": "barnesHut",
                    "timestep": 0.5
                },
                "nodes": {
                    "font": {"size": 14, "color": "#ffffff"},
                    "borderWidth": 2,
                    "shadow": True
                },
                "edges": {
                    "font": {"size": 11, "color": "#aaaaaa", "align": "middle"},
                    "color": {"color": "#555555", "highlight": "#1E88E5"},
                    "arrows": {"to": {"enabled": True, "scaleFactor": 0.7}},
                    "smooth": {"type": "curvedCW", "roundness": 0.2}
                },
                "interaction": {
                    "hover": True,
                    "navigationButtons": True,
                    "tooltipDelay": 100
                }
            }
            net.set_options(json.dumps(physics_config))

            color_map = {
                "Company": "#1E88E5",
                "Account": "#D32F2F",
                "Person": "#388E3C",
                "Invoice": "#FBC02D",
                "Transaction": "#F57C00",
                "Document": "#7B1FA2",
            }

            for node, data in g_sub.nodes(data=True):
                lbl = data.get("label", str(node))
                ntype = data.get("node_type", "Entity")
                color = color_map.get(ntype, "#888888")
                
                title_tooltip = f"<b>{lbl}</b><br>ID: {node}<br>Type: {ntype}"
                if "document_id" in data:
                    title_tooltip += f"<br>Doc: {data['document_id']}"
                if "amount" in data:
                    title_tooltip += f"<br>Amount: ${data['amount']:,.2f}"

                net.add_node(
                    node,
                    label=lbl,
                    title=title_tooltip,
                    color=color,
                    shape="dot" if ntype in ["Company", "Account"] else "ellipse",
                    size=22 if ntype == "Company" else 16
                )

            for u, v, d in g_sub.edges(data=True):
                rel = d.get("relation_type", "TRANSFERRED")
                amt = d.get("amount", 0.0)
                edge_label = f"${amt:,.0f}" if amt > 0 else rel
                edge_title = f"{rel}: ${amt:,.2f}" if amt > 0 else rel
                net.add_edge(u, v, label=edge_label, title=edge_title)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
                net.save_graph(tmp.name)
                with open(tmp.name, "r", encoding="utf-8") as f:
                    html_content = f.read()

            components.html(html_content, height=670, scrolling=False)

        except Exception as e:
            st.error(f"Pyvis rendering error: {e}. Falling back to Plotly engine.")

    else:
        k_factor = 3.5 * (node_spacing / 5.0) / (np.sqrt(max(1, g_sub.number_of_nodes())))
        pos = nx.spring_layout(g_sub, k=k_factor, iterations=120, seed=42)

        edge_x, edge_y = [], []
        for edge in g_sub.edges():
            if edge[0] in pos and edge[1] in pos:
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1.2, color='#666666'),
            hoverinfo='none',
            mode='lines'
        )

        node_x, node_y, node_hover, node_colors, node_sizes, node_labels = [], [], [], [], [], []
        color_map = {
            "Company": "#1E88E5",
            "Account": "#D32F2F",
            "Person": "#388E3C",
            "Invoice": "#FBC02D",
            "Transaction": "#F57C00",
            "Document": "#7B1FA2",
        }

        for node in g_sub.nodes():
            if node in pos:
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                lbl = g_sub.nodes[node].get("label", str(node))
                ntype = g_sub.nodes[node].get("node_type", "Unknown")
                
                node_labels.append(lbl)
                node_hover.append(f"<b>{lbl}</b><br>ID: {node}<br>Type: {ntype}")
                node_colors.append(color_map.get(ntype, "#888888"))
                node_sizes.append(24 if ntype == "Company" else 18)

        show_labels = st.checkbox("Toggle Node Text Labels", value=True)

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text' if show_labels else 'markers',
            hoverinfo='text',
            text=node_labels,
            textposition="top center",
            textfont=dict(size=12, color="white"),
            hovertext=node_hover,
            marker=dict(
                color=node_colors,
                size=node_sizes,
                line=dict(width=2, color="white")
            )
        )

        fig_net = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                title='Clean Non-Overlapping Spacing Graph',
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                paper_bgcolor='#0E1117',
                plot_bgcolor='#0E1117',
                height=650,
            )
        )
        st.plotly_chart(fig_net, use_container_width=True)

    # Path Tracing Tool
    st.markdown("---")
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
                    st.code(" ➔ ".join(p))
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
# TAB 5: INDIAN CA TAX AUDIT & STATUTORY COMPLIANCE (NEW DOMAIN MODULE)
# ==============================================================================
with tab5:
    st.header("🇮🇳 Indian Income Tax (1961) & GST Act (2017) CA Audit Module")
    st.caption("Assists Chartered Accountants (CAs) during Statutory Audit, Tax Audit u/s 44AB (Form 3CD), and GST Fraud Risk Analysis.")

    metrics = ca_audit_results.get("summary_metrics", {})
    
    # Statutory KPI Metrics (in INR ₹)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Sec 40A(3) Disallowance", f"₹{metrics.get('total_sec_40a3_disallowance', 0):,.2f}", delta="Tax Audit Clause 21(b)", delta_color="inverse")
    m2.metric("Sec 269SS/269T Risk", f"₹{metrics.get('total_sec_269ss_penalty_exposure', 0):,.2f}", delta="Clause 31(a)/(b) 100% Penalty", delta_color="inverse")
    m3.metric("GST Circular ITC Risk", f"₹{metrics.get('total_gst_circular_itc_at_risk', 0):,.2f}", delta="CGST Sec 16(2)/132", delta_color="inverse")
    m4.metric("Total Tax Audit Findings", metrics.get("total_flagged_tax_items", 0), delta="ICAI SA 240 Fraud Risk")

    st.markdown("---")
    st.subheader("📋 Form 3CD Tax Audit Report Clause Mappings")

    c_tab1, c_tab2, c_tab3 = st.tabs([
        "Clause 21(b): Sec 40A(3) Cash Disallowance",
        "Clause 31(a)/(b): Sec 269SS/269T Cash Loans",
        "CGST Act: Circular Trading & ITC Reversal",
    ])

    with c_tab1:
        st.markdown("**Income Tax Act, 1961 — Section 40A(3) Cash Payments Exceeding ₹10,000/day**")
        c21b = ca_audit_results.get("form_3cd_clause_21b", [])
        if c21b:
            st.dataframe(pd.DataFrame(c21b), use_container_width=True)
        else:
            st.success("No Section 40A(3) cash disallowances detected in audited evidence.")

    with c_tab2:
        st.markdown("**Income Tax Act, 1961 — Section 269SS & 269T Cash Loans/Deposits Accepted or Repaid >= ₹20,000**")
        c31a = ca_audit_results.get("form_3cd_clause_31a", [])
        c31b = ca_audit_results.get("form_3cd_clause_31b", [])
        combined_31 = c31a + c31b
        if combined_31:
            st.dataframe(pd.DataFrame(combined_31), use_container_width=True)
        else:
            st.success("No Section 269SS/269T cash loan violations detected.")

    with c_tab3:
        st.markdown("**CGST Act, 2017 — Circular Trading & Bogus Invoice Input Tax Credit (ITC) Fraud u/s 16(2)(c) & Sec 132**")
        gst_r = ca_audit_results.get("gst_itc_risks", [])
        if gst_r:
            st.dataframe(pd.DataFrame(gst_r), use_container_width=True)
        else:
            st.success("No circular trading ITC risks detected under GST Laws.")

    st.markdown("---")
    st.subheader("📄 Export ICAI SA 240/250 Tax Audit Working Paper (W/P)")
    
    ca_engine = IndianCATaxAuditEngine()
    wp_markdown = ca_engine.generate_ca_working_paper_md(ca_audit_results, entity_name="Audited Client Assessee", ay="2026-27")
    
    st.download_button(
        label="📥 Download Official CA Tax Audit Working Paper (.MD)",
        data=wp_markdown,
        file_name="CA_Tax_Audit_Working_Paper_AY2026-27.md",
        mime="text/markdown",
        use_container_width=True,
    )

# ==============================================================================
# TAB 6: POLICY RAG VERIFICATION
# ==============================================================================
with tab6:
    st.header("RAG Policy Verification & Compliance Engine")
    
    st.subheader("🔍 Query Internal & Statutory Policy Vector Database (ChromaDB)")
    policy_query = st.text_input("Enter statutory policy query (Income Tax / GST / AML):", "Section 269SS Section 40A(3) GST circular trading ITC disallowance")
    
    if policy_query:
        p_store = get_orchestrator().policy_store
        retrieved = p_store.search_policies(policy_query, top_k=4)
        
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
# TAB 7: AUDIT LEDGER & REPORT
# ==============================================================================
with tab7:
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
