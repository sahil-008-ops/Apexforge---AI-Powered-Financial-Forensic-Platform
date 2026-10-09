"""
ApexForge Streamlit Investigation Platform
Interactive Forensic Auditing & Transaction-Tracing Dashboard
Featuring Severity Level Anomaly Segregation, Indian CA Audit Resolution Workflow, All-Format Document Ingestion,
and Indian Income Tax (1961) & GST Act (2017) Compliance Engine.
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
    AnomalySeverity,
)
from apexforge.ingestion.document_loader import DocumentLoader
from apexforge.generator.synthetic_data import SyntheticDataGenerator
from apexforge.agents.orchestrator import ForensicOrchestrator
from apexforge.graph.graph_store import TransactionGraphStore
from apexforge.rag.policy_store import RAGPolicyStore
from apexforge.ca_audit.ca_tax_engine import IndianCATaxAuditEngine
from apexforge.ledger_generation.auto_ledger import AutoLedgerGenerator
from apexforge.reconciliation.bank_reconciliation import BankReconciliationEngine
from apexforge.reconciliation.ais_reconciliation import AISReconciliationEngine
from apexforge.reconciliation.unified_reconciliation import UnifiedReconciliationEngine
from apexforge.copilot.ca_copilot import CAInvestigationCopilot
from apexforge.ca_audit.paper_generator import CAReviewWorkflow, AuditWorkingPaperGenerator
from apexforge.models.data_models import AuditReviewStatus


st.set_page_config(
    page_title="ApexForge — Indian CA Forensic & Tax Audit Platform",
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
    should_reset = False
    if "results" not in st.session_state:
        should_reset = True
    else:
        results = st.session_state["results"]
        if "anomalies" in results and results["anomalies"]:
            for a in results["anomalies"]:
                # Reset cached session state if old dollar signs or generic fallbacks exist
                exp = getattr(a, "expected_baseline", "")
                expl = getattr(a, "explanation", "")
                if "$" in expl or "$" in exp or not exp or exp == "Standard Indian Statutory Compliance Benchmark":
                    should_reset = True
                    break

    if should_reset:
        gen = SyntheticDataGenerator(seed=42)
        docs = gen.generate_benchmark_dataset()
        orch = get_orchestrator()
        st.session_state["results"] = orch.run_investigation_pipeline(docs)


initialize_session()

# Sidebar Control Panel
st.sidebar.image("https://img.icons8.com/color/96/000000/shield-with-authorization.png", width=64)
st.sidebar.title("ApexForge Platform")
st.sidebar.caption("AI Forensic & CA Tax Audit Engine v1.8 (INR Standard)")

st.sidebar.markdown("---")
st.sidebar.subheader("Benchmark Datasets")
if st.sidebar.button("🚀 Run 50-Doc Fraud Benchmark (₹ INR)", use_container_width=True):
    with st.spinner("Executing CA investigation across 50 benchmark documents..."):
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
st.markdown('<div class="sub-header">AI-Powered Forensic Financial Auditing, Transaction Tracing & Indian CA Tax Audit Platform</div>', unsafe_allow_html=True)

# Navigation Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12, tab13 = st.tabs([
    "📊 Executive Summary",
    "📁 Multi-File Ingestion",
    "🕸️ Clean Transaction Graph",
    "🚨 Segregated Anomalies & Deviations",
    "🇮🇳 CA Tax Audit (Income Tax & GST)",
    "📜 Policy RAG Verification",
    "📒 AI Auto Ledger",
    "🏦 Bank Reconciliation",
    "📜 AIS & 26AS Reconciliation",
    "🔍 360° Multi-Way Matrix",
    "🤖 CA Forensic Copilot",
    "📁 ICAI Audit Working Papers",
    "🔐 SHA3-256 Audit Trail",
])

# ==============================================================================
# TAB 1: EXECUTIVE SUMMARY
# ==============================================================================
with tab1:
    st.header("Executive Audit Investigation Overview")
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    total_vol = sum(t.amount for t in transactions)
    crit_count = sum(1 for a in anomalies if a.severity.value == "CRITICAL")
    open_count = sum(1 for a in anomalies if getattr(a, "status", "OPEN") == "OPEN")
    
    col1.metric("Ingested Docs", len(docs))
    col2.metric("Extracted Entities", len(entities))
    col3.metric("Transactions", len(transactions))
    col4.metric("Total Volume (₹)", f"₹{total_vol:,.0f}")
    col5.metric("Circular Loops", len(cycles), delta=f"{len(cycles)} loops", delta_color="inverse")
    col6.metric("Unresolved Variances", open_count, delta=f"{open_count} Open", delta_color="inverse")
    
    st.markdown("---")
    st.subheader("🤖 Executive Forensic Narrative Summary")
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
        min_tx_val = st.slider("Min Transaction Value (₹)", 0, 1000000, 0, step=50000)
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
                    title_tooltip += f"<br>Amount: ₹{data['amount']:,.2f} INR"

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
                edge_label = f"₹{amt:,.0f}" if amt > 0 else rel
                edge_title = f"{rel}: ₹{amt:,.2f}" if amt > 0 else rel
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
# TAB 4: SEGREGATED ANOMALIES & AUDITOR VARIANCE CORRECTION WORKFLOW
# ==============================================================================
with tab4:
    st.header("🚨 Segregated Anomaly & Forensic Variance Engine")
    st.caption("Anomalies grouped by Severity Tiers with Indian Statutory Law (Income Tax 1961 & CGST Act 2017) Deviation Analysis.")

    crit_list = [a for a in anomalies if a.severity == AnomalySeverity.CRITICAL]
    high_list = [a for a in anomalies if a.severity == AnomalySeverity.HIGH]
    med_list = [a for a in anomalies if a.severity == AnomalySeverity.MEDIUM]
    low_list = [a for a in anomalies if a.severity == AnomalySeverity.LOW]

    sev_c1, sev_c2, sev_c3, sev_c4 = st.columns(4)
    sev_c1.metric("🔴 CRITICAL Severity", len(crit_list), delta="Immediate Audit Priority", delta_color="inverse")
    sev_c2.metric("🟠 HIGH Severity", len(high_list), delta="High Financial Exposure", delta_color="inverse")
    sev_c3.metric("🟡 MEDIUM Severity", len(med_list), delta="Documentation Defect")
    sev_c4.metric("🟢 LOW Severity", len(low_list), delta="Minor Discrepancy")

    st.markdown("---")
    st.subheader("🔍 Severity Level Segregation & Auditor Resolution Controls")

    s_tab1, s_tab2, s_tab3, s_tab4, s_tab5 = st.tabs([
        f"📋 All Anomalies ({len(anomalies)})",
        f"🔴 CRITICAL ({len(crit_list)})",
        f"🟠 HIGH ({len(high_list)})",
        f"🟡 MEDIUM ({len(med_list)})",
        f"🟢 LOW ({len(low_list)})",
    ])

    def render_anomaly_cards_with_resolution(anomaly_group: List[AnomalyFinding], tab_prefix: str = "all"):
        if not anomaly_group:
            st.info("No anomalies in this severity category.")
            return

        for idx, a in enumerate(anomaly_group):
            exp_base = getattr(a, "expected_baseline", "") or "Linear commercial supply chain flow u/s 16(2) / Income Tax Act baseline"
            obs_val = getattr(a, "observed_value", "") or f"Recorded Evidence Payload (Amount: ₹{a.supporting_features.get('amount', 0):,.2f} INR)"
            dev_delta = getattr(a, "deviation_delta", "") or "Deviates from established CGST / Income Tax statutory threshold"
            ev_loc = getattr(a, "evidence_location", "") or f"Doc ID: {', '.join(a.evidence_documents)}"
            aud_rec = getattr(a, "audit_recommendation", "") or "Audit evidence document and issue Form 3CD Clause 21(b)/31(a) qualification."
            astatus = getattr(a, "status", "OPEN")

            status_badge = "🟢 CORRECTED" if astatus != "OPEN" else "🔴 OPEN VARIANCE"

            # Clean explanation from old dollar signs if any remain in text
            clean_explanation = a.explanation.replace("$", "₹")

            with st.expander(f"[{a.severity.value}] {a.anomaly_type.value} — ID: {a.anomaly_id} ({status_badge})", expanded=(idx < 2)):
                st.markdown(f"**Explanation:** {clean_explanation}")
                
                st.markdown("##### 📊 Forensic Deviation Breakdown (Where Transaction Defers)")
                d1, d2 = st.columns(2)
                with d1:
                    st.markdown(f"🎯 **Expected Statutory Baseline:** `{exp_base}`")
                    st.markdown(f"🔍 **Observed Evidence Value:** `{obs_val}`")
                with d2:
                    st.markdown(f"📈 **Variance / Deviation Delta:** `{dev_delta}`")
                    st.markdown(f"📍 **Evidence Document Pointer:** `{ev_loc}`")

                st.markdown(f"💡 **CA Audit Recommendation:** {aud_rec}")
                
                # HUMAN CA AUDITOR VARIANCE CORRECTION FORM WITH TAB UNIQUE KEYS
                st.markdown("---")
                st.markdown(f"##### 🛠️ Human CA Auditor Variance Resolution Form (ID: `{a.anomaly_id}`)")
                
                if astatus != "OPEN":
                    st.success(f"✅ Variance Corrected: **{astatus}** | Signed by: `{getattr(a, 'resolved_by', 'CA Auditor')}` at `{getattr(a, 'resolved_timestamp', '')[:19]}`")
                    st.markdown(f"**Auditor Notes:** {getattr(a, 'auditor_resolution_notes', '')}")

                unique_form_key = f"res_form_{tab_prefix}_{a.anomaly_id}"
                with st.form(key=unique_form_key):
                    f_col1, f_col2 = st.columns(2)
                    with f_col1:
                        action_choice = st.selectbox(
                            "Select CA Audit Correction Action",
                            [
                                "CORRECTED_DISALLOWED_IN_PGBP",
                                "GST_ITC_REVERSED",
                                "SUBSTANTIATED_WITH_DOCS",
                                "RESOLVED_COMMERCIAL_EXPEDIENCY",
                                "REPORTED_TO_FIU_STR"
                            ],
                            key=f"act_{tab_prefix}_{a.anomaly_id}"
                        )
                        auditor_name_input = st.text_input("Auditor / CA Name", "CA Statutory Auditor", key=f"aud_{tab_prefix}_{a.anomaly_id}")
                    with f_col2:
                        notes_input = st.text_area("Auditor Resolution Notes & Form 3CD Clause References", "Rectified variance u/s 40A(3) / GST Sec 16(2).", key=f"not_{tab_prefix}_{a.anomaly_id}")
                    
                    submit_res = st.form_submit_button("✍️ Apply CA Audit Correction & Sign SHA3-256 Ledger")
                    if submit_res:
                        orch = get_orchestrator()
                        success = orch.resolve_anomaly_variance(
                            results=results,
                            anomaly_id=a.anomaly_id,
                            resolution_action=action_choice,
                            notes=notes_input,
                            auditor_name=auditor_name_input,
                        )
                        if success:
                            st.success(f"Successfully corrected variance {a.anomaly_id} and recorded block in SHA3-256 Ledger!")
                            st.rerun()

    with s_tab1:
        render_anomaly_cards_with_resolution(anomalies, tab_prefix="all")
    with s_tab2:
        render_anomaly_cards_with_resolution(crit_list, tab_prefix="crit")
    with s_tab3:
        render_anomaly_cards_with_resolution(high_list, tab_prefix="high")
    with s_tab4:
        render_anomaly_cards_with_resolution(med_list, tab_prefix="med")
    with s_tab5:
        render_anomaly_cards_with_resolution(low_list, tab_prefix="low")

    st.markdown("---")
    st.subheader("🔄 Detected Circular Transaction Loops")
    if cycles:
        cycle_table = []
        for c in cycles:
            cycle_table.append({
                "Cycle ID": c.cycle_id,
                "Cycle Path": " ➔ ".join([e.split(" ")[0] for e in c.entities_involved]),
                "Total Volume (₹)": f"₹{c.total_amount:,.2f}",
                "Hop Length": c.cycle_length,
                "Risk Classification": c.risk_level,
                "Source Docs": ", ".join(c.source_documents),
            })
        st.dataframe(pd.DataFrame(cycle_table), use_container_width=True)
    else:
        st.info("No closed transaction cycles detected in graph.")

# ==============================================================================
# TAB 5: INDIAN CA TAX AUDIT & STATUTORY COMPLIANCE
# ==============================================================================
with tab5:
    st.header("🇮🇳 Indian Income Tax (1961) & GST Act (2017) CA Audit Module")
    st.caption("Assists Chartered Accountants (CAs) during Statutory Audit, Tax Audit u/s 44AB (Form 3CD), and GST Fraud Risk Analysis.")

    metrics = ca_audit_results.get("summary_metrics", {})
    
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
# TAB 7: AI AUTOMATIC LEDGER GENERATION (MODULE B)
# ==============================================================================
with tab7:
    st.header("📒 AI Automatic Double-Entry Ledger Generation Engine")
    st.caption("Classifies bank statements & invoices into Double-Entry Accounting Ledgers with Indian GST & TDS mappings.")

    auto_ledger_gen = AutoLedgerGenerator()
    generated_ledgers = auto_ledger_gen.generate_ledger_entries(transactions)

    cat_summary = auto_ledger_gen.get_summary_by_category()
    sc1, sc2, sc3, sc4, sc5 = st.columns(5)
    sc1.metric("Total Ledger Entries", len(generated_ledgers))
    sc2.metric("Sales / Revenue (₹)", f"₹{cat_summary.get('Revenue / Sales', 0.0):,.2f}")
    sc3.metric("Purchases (₹)", f"₹{cat_summary.get('Direct Purchase / Cost of Sales', 0.0):,.2f}")
    sc4.metric("Indirect Expenses (₹)", f"₹{cat_summary.get('Indirect Administrative Expense', 0.0):,.2f}")
    sc5.metric("Capital Assets (₹)", f"₹{cat_summary.get('Fixed / Capital Asset', 0.0):,.2f}")

    st.markdown("---")
    st.subheader("📋 Generated General Ledger Entries & Statutory Tax Mappings")

    ledger_table_data = []
    for entry in generated_ledgers:
        ledger_table_data.append({
            "Entry ID": entry.entry_id,
            "Date": entry.date,
            "Description": entry.description,
            "Debit Account": entry.debit_account,
            "Credit Account": entry.credit_account,
            "Amount (₹)": f"₹{entry.amount:,.2f}",
            "Category": entry.category.value,
            "GST Rate": f"{entry.gst_rate}%",
            "ITC Eligible": "YES" if entry.itc_eligible else "NO",
            "TDS Section": entry.tds_section or "N/A",
            "AI Confidence": f"{entry.confidence_score * 100:.0f}%",
            "CA Status": entry.status.value,
        })

    st.dataframe(pd.DataFrame(ledger_table_data), use_container_width=True)

# ==============================================================================
# TAB 8: BANK RECONCILIATION ENGINE (MODULE C)
# ==============================================================================
with tab8:
    st.header("🏦 Bank Statement Reconciliation Engine")
    st.caption("Matches Bank Statement line items against Books of Accounts (Ledgers), identifying unrecorded charges & timing variances.")

    bank_engine = BankReconciliationEngine()
    reconciled_lines = bank_engine.reconcile(transactions, generated_ledgers)
    rec_summary = bank_engine.get_reconciliation_summary()

    rc1, rc2, rc3, rc4, rc5 = st.columns(5)
    rc1.metric("Total Statement Lines", rec_summary["total_line_items"])
    rc2.metric("Fully Matched", rec_summary["matched_count"], delta=f"{rec_summary['matched_count']} Matched")
    rc3.metric("Unmatched Bank Lines", rec_summary["unmatched_bank_count"], delta="Needs Posting", delta_color="inverse")
    rc4.metric("Unmatched Books Entries", rec_summary["unmatched_ledger_count"], delta="Unpresented Cheques", delta_color="off")
    rc5.metric("Reconciled Amount (₹)", f"₹{rec_summary['reconciled_amount_inr']:,.2f}")

    st.markdown("---")
    st.subheader("🔍 Bank Reconciliation Breakdown & Audit Recommendations")

    rec_table_data = []
    for line in reconciled_lines:
        rec_table_data.append({
            "Line ID": line.line_id,
            "Bank Date": line.bank_date or "-",
            "Ledger Date": line.ledger_date or "-",
            "Bank Statement Description": line.bank_description,
            "Books Ledger Description": line.ledger_description or "-",
            "Bank Amount (₹)": f"₹{line.bank_amount:,.2f}",
            "Ledger Amount (₹)": f"₹{line.ledger_amount:,.2f}",
            "Variance (₹)": f"₹{line.variance:,.2f}",
            "Reconciliation Status": line.status.value,
            "CA Recommendation": line.recommendation,
        })

    st.dataframe(pd.DataFrame(rec_table_data), use_container_width=True)

# ==============================================================================
# TAB 9: AIS & FORM 26AS TAX RECONCILIATION (MODULE D)
# ==============================================================================
with tab9:
    st.header("📜 Income Tax AIS & Form 26AS Reconciliation Engine")
    st.caption("Reconciles Income Tax AIS SFT codes & 26AS TDS credits against Books & Bank Statements to prevent Sec 68 / 115BBE assessments.")

    ais_engine = AISReconciliationEngine(pan="AAACA1234F", financial_year="FY 2024-25")
    ais_records = ais_engine.reconcile_with_books(generated_ledgers, transactions)
    ais_summary = ais_engine.get_ais_summary()

    ac1, ac2, ac3, ac4 = st.columns(4)
    ac1.metric("Assessee PAN", ais_summary["pan"])
    ac2.metric("Total AIS Reported (₹)", f"₹{ais_summary['total_reported_amount_inr']:,.2f}")
    ac3.metric("Books Recorded (₹)", f"₹{ais_summary['total_book_recorded_inr']:,.2f}")
    ac4.metric("Unreported Income Discrepancy", f"₹{ais_summary['unreported_income_variance_inr']:,.2f}", delta=f"{ais_summary['high_risk_discrepancies']} High Risk", delta_color="inverse")

    st.markdown("---")
    st.subheader("📌 AIS SFT Information Codes & Statutory Mismatch Analysis")

    ais_table_data = []
    for ar in ais_records:
        ais_table_data.append({
            "Record ID": ar.record_id,
            "Info Code": ar.info_code,
            "Description": ar.info_description,
            "Source Reporter": ar.source_reporter,
            "AIS Reported (₹)": f"₹{ar.reported_amount:,.2f}",
            "Book Amount (₹)": f"₹{ar.book_recorded_amount:,.2f}",
            "Variance (₹)": f"₹{ar.variance_amount:,.2f}",
            "Statutory Disallowance Section": ar.disallowance_section,
            "Compliance Risk": ar.compliance_risk,
        })

    st.dataframe(pd.DataFrame(ais_table_data), use_container_width=True)

# ==============================================================================
# TAB 10: 360° UNIFIED MULTI-WAY RECONCILIATION MATRIX (MODULE F)
# ==============================================================================
with tab10:
    st.header("🔍 360° Unified Multi-Way Forensic Reconciliation Matrix")
    st.caption("Cross-verifies Bank Statement ↔ Books ↔ AIS ↔ Invoices ↔ Graph Cycles into a single forensic compliance view.")

    unified_engine = UnifiedReconciliationEngine()
    matrix = unified_engine.build_unified_matrix(transactions, generated_ledgers, reconciled_lines, ais_records, cycles)
    matrix_summary = unified_engine.get_unified_summary()

    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric("Total Evaluated Transactions", matrix_summary["total_matrix_entries"])
    mc2.metric("Fully Reconciled & Compliant", matrix_summary["reconciled_fully"])
    mc3.metric("Critical Forensic Flags", matrix_summary["critical_forensic_flags"], delta_color="inverse")
    mc4.metric("Total Flagged Exposure (₹)", f"₹{matrix_summary['total_flagged_amount_inr']:,.2f}")

    st.markdown("---")
    st.subheader("📊 5-Dimension Compliance Matrix")

    matrix_table = []
    for m in matrix:
        matrix_table.append({
            "Matrix ID": m.matrix_id,
            "Counterparty": m.counterparty,
            "Amount (₹)": f"₹{m.amount:,.2f}",
            "Bank Matched": "✅" if m.bank_reconciled else "❌",
            "Ledger Posted": "✅" if m.ledger_posted else "❌",
            "AIS Matched": "✅" if m.ais_matched else "❌",
            "Invoice Backed": "✅" if m.invoice_backed else "❌",
            "Graph Cycle": "🚨 YES" if m.graph_cycle_detected else "✅ NO",
            "Risk Score": f"{m.forensic_risk_score * 100:.0f}%",
            "Unified Status": m.unified_status,
            "CA Audit Action": m.audit_action,
        })

    st.dataframe(pd.DataFrame(matrix_table), use_container_width=True)

# ==============================================================================
# TAB 11: CA FORENSIC INVESTIGATION COPILOT (MODULE G)
# ==============================================================================
with tab11:
    st.header("🤖 CA Forensic Investigation Copilot")
    st.caption("Evidence-grounded natural language query assistant for Indian Income Tax, CGST Law, and ICAI Auditing Standards.")

    copilot = CAInvestigationCopilot()

    st.markdown("#### 💡 Quick Statutory Query Presets")
    qp1, qp2, qp3 = st.columns(3)
    preset_query = ""
    if qp1.button("📜 Explain CGST Sec 16(2) ITC Circular Disallowance", use_container_width=True):
        preset_query = "Explain CGST Sec 16(2) ITC disallowance for circular trading"
    if qp2.button("💵 Check Cash Expense Limits u/s 40A(3) & 269SS", use_container_width=True):
        preset_query = "What are the rules for cash payments u/s 40A(3) and loans u/s 269SS?"
    if qp3.button("📊 Investigate AIS Unreported Income u/s 68", use_container_width=True):
        preset_query = "Tell me about AIS unreported income u/s 68 and Sec 115BBE"

    query_input = st.text_input("Enter your forensic audit query:", value=preset_query or "Explain CGST Sec 16(2) ITC disallowance for circular trading")

    if query_input:
        with st.spinner("Analyzing statutory evidence & searching policy store..."):
            answer_dict = copilot.query(query_input, anomalies=anomalies, cycles=cycles, ais_records=ais_records)

            st.markdown(answer_dict["answer"])

            st.markdown("---")
            st.subheader("📚 Statutory Citations & Evidence Sources")
            for cit in answer_dict["policy_citations"]:
                st.info(f"📌 {cit}")
            for ev in answer_dict["evidence_sources"]:
                st.caption(f"📍 Document Reference: `{ev}`")

# ==============================================================================
# TAB 12: ICAI AUDIT WORKING PAPERS (MODULE I & H)
# ==============================================================================
with tab12:
    st.header("📁 ICAI Audit Working Papers (SA 240 / SA 250 / Form 3CD)")
    st.caption("Generates ICAI SA 240 (Fraud Risk Assessment) & SA 250 (Law Compliance) audit working papers with CA review controls.")

    wp_gen = AuditWorkingPaperGenerator(ledger=ledger)
    working_paper = wp_gen.generate_working_paper(anomalies)

    wpc1, wpc2, wpc3 = st.columns(3)
    wpc1.metric("Working Paper ID", working_paper.paper_id)
    wpc2.metric("Financial Year", working_paper.financial_year)
    wpc3.metric("Audit Ledger Verification", working_paper.tamper_hash_chain_status)

    st.markdown("---")
    st.subheader("🛡️ ICAI SA 240: Fraud Risk Audit Findings")
    for f in working_paper.sa240_fraud_findings:
        st.error(f)

    st.markdown("---")
    st.subheader("⚖️ ICAI SA 250: Statutory Laws & Regulations Compliance")
    for s in working_paper.sa250_statutory_compliance:
        st.warning(s)

    st.markdown("---")
    st.subheader("📊 Tax Audit Working Paper Schedules (Form 3CD & CGST Act)")
    for sch in working_paper.schedules:
        with st.expander(f"📍 [{sch.statutory_clause}] {sch.schedule_name}"):
            st.markdown(f"**🤖 System Detection:** {sch.system_findings_summary}")
            st.markdown(f"**🔍 CA Auditor Observation:** {sch.ca_auditor_observations}")
            st.markdown(f"**💡 CA Final Audit Conclusion:** `{sch.ca_auditor_conclusion}`")

    st.markdown("---")
    wp_md = wp_gen.export_working_paper_markdown(working_paper)
    st.download_button(
        label="📥 Download Official ICAI SA 240/250 Audit Working Paper (.MD)",
        data=wp_md,
        file_name=f"ICAI_Audit_Working_Paper_{working_paper.paper_id}.md",
        mime="text/markdown",
        use_container_width=True,
    )

# ==============================================================================
# TAB 13: SHA3-256 TAMPER-EVIDENT AUDIT TRAIL (MODULE A)
# ==============================================================================
with tab13:
    st.header("🔐 Tamper-Evident SHA3-256 Audit Ledger & Event Trail")
    st.caption("Append-only court-oriented ledger capturing all system events, AI determinations, and manual CA corrections with cryptographic hash chaining.")

    col_l1, col_l2 = st.columns([2, 1])

    with col_l1:
        st.subheader("🔐 Ledger & Event Chain Verification")

        is_valid_l, count_l, _, msg_l = ledger.verify_chain_integrity()
        is_valid_e, count_e, _, msg_e = ledger.verify_event_chain_integrity()

        if is_valid_l and is_valid_e:
            st.success(f"✅ HASH CHAIN VERIFIED: Standard Ledger ({count_l} Entries) | Audit Event Ledger ({count_e} Events)")
        else:
            st.error(f"❌ TAMPER DETECTED: Ledger ({msg_l}) | Events ({msg_e})")

        st.markdown("#### Standard Audit Ledger Blocks")
        st.dataframe(pd.DataFrame(ledger.export_ledger_dict()), use_container_width=True)

        st.markdown("#### Granular User & CA Action Events")
        st.dataframe(pd.DataFrame(ledger.export_events_dict()), use_container_width=True)

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
    st.subheader("📄 Full Forensic Audit Investigation Report")

    report_text = f"""# FORENSIC AUDIT INVESTIGATION REPORT
**Generated by ApexForge CA Audit Platform**
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

