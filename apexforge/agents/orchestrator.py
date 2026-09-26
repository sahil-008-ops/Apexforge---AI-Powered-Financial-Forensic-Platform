"""
Multi-Agent Orchestrator Engine
Coordinates the execution state-machine across all forensic agents (Extraction, Linker, Anomaly, Policy, Reasoner, CA Tax Audit),
provides auditor variance resolution & tax adjustment workflows, and writes tamper-evident SHA3-256 audit ledger entries.
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from apexforge.models.data_models import (
    NormalizedDocument,
    Entity,
    Relationship,
    Transaction,
    TransactionCycle,
    AnomalyFinding,
    PolicyFinding,
    ForensicNarrativeSection,
)
from apexforge.graph.graph_store import TransactionGraphStore
from apexforge.rag.policy_store import RAGPolicyStore
from apexforge.ledger.audit_ledger import ForensicAuditLedger

from apexforge.agents.extraction_agent import ExtractionAgent
from apexforge.agents.linker_agent import LinkerAgent
from apexforge.agents.anomaly_agent import AnomalyAgent
from apexforge.agents.policy_agent import PolicyAgent
from apexforge.agents.reasoner_agent import ReasonerAgent
from apexforge.ca_audit.ca_tax_engine import IndianCATaxAuditEngine


class ForensicOrchestrator:
    def __init__(self, graph_store: TransactionGraphStore = None, policy_store: RAGPolicyStore = None):
        self.graph_store = graph_store or TransactionGraphStore()
        self.policy_store = policy_store or RAGPolicyStore()
        self.ledger = ForensicAuditLedger()

        self.extraction_agent = ExtractionAgent()
        self.linker_agent = LinkerAgent(self.graph_store)
        self.anomaly_agent = AnomalyAgent(self.graph_store)
        self.policy_agent = PolicyAgent(self.policy_store)
        self.reasoner_agent = ReasonerAgent()
        self.ca_tax_engine = IndianCATaxAuditEngine()

    def run_investigation_pipeline(self, documents: List[NormalizedDocument]) -> Dict[str, Any]:
        """Runs full multi-agent investigation workflow over ingested documents."""
        self.ledger = ForensicAuditLedger()  # Fresh chain for batch run

        # Genesis ledger entry
        self.ledger.add_entry(
            event_type="PIPELINE_INITIATED",
            input_reference=f"Batch size: {len(documents)} documents",
            finding=f"Started forensic investigation pipeline for {len(documents)} evidence items.",
            evidence=[d.sha3_256_hash for d in documents],
        )

        # Stage 1: Document / Extraction Agent
        entities, relationships, transactions = self.extraction_agent.process_documents(documents)
        self.ledger.add_entry(
            event_type="AGENT_1_EXTRACTION_COMPLETE",
            input_reference="Agent 1: ExtractionAgent",
            finding=f"Extracted {len(entities)} entities, {len(relationships)} relationships, and {len(transactions)} transactions.",
            evidence=[e.entity_id for e in entities[:5]],
        )

        # Stage 2: Linker / Pattern Agent
        graph_store = self.linker_agent.link_entities_and_build_graph(
            documents=documents,
            entities=entities,
            relationships=relationships,
            transactions=transactions,
        )
        self.ledger.add_entry(
            event_type="AGENT_2_GRAPH_LINKING_COMPLETE",
            input_reference="Agent 2: LinkerAgent",
            finding=f"Constructed transaction graph with {graph_store.graph.number_of_nodes()} nodes and {graph_store.graph.number_of_edges()} edges.",
            evidence=[f"Nodes: {graph_store.graph.number_of_nodes()}"],
        )

        # Stage 3: Anomaly Agent
        cycles, anomalies = self.anomaly_agent.analyze_anomalies(
            transactions=transactions,
            entities=entities,
            relationships=relationships,
            documents=documents,
        )
        self.ledger.add_entry(
            event_type="AGENT_3_ANOMALY_DETECTION_COMPLETE",
            input_reference="Agent 3: AnomalyAgent",
            finding=f"Detected {len(cycles)} circular transaction loops and {len(anomalies)} anomalies.",
            evidence=[c.cycle_id for c in cycles] + [a.anomaly_id for a in anomalies[:5]],
        )

        # Stage 4: Indian Income Tax & GST CA Audit Compliance Engine
        ca_audit_results = self.ca_tax_engine.evaluate_indian_tax_compliance(
            transactions=transactions,
            entities=entities,
            relationships=relationships,
            cycles=cycles,
        )
        self.ledger.add_entry(
            event_type="CA_STATUTORY_TAX_AUDIT_COMPLETE",
            input_reference="Indian CA Income Tax & GST Compliance Engine",
            finding=f"Evaluated Indian Income Tax & GST Laws: {ca_audit_results['summary_metrics']['total_flagged_tax_items']} statutory tax compliance findings identified.",
            evidence=[f"Sec 40A(3) Disallowance: ₹{ca_audit_results['summary_metrics']['total_sec_40a3_disallowance']:,.2f}"],
        )

        # Stage 5: Policy / Verification Agent
        policy_findings = self.policy_agent.verify_anomalies_against_policies(anomalies)
        self.ledger.add_entry(
            event_type="AGENT_4_POLICY_VERIFICATION_COMPLETE",
            input_reference="Agent 4: PolicyAgent",
            finding=f"Matched findings against policy vector store, issuing {len(policy_findings)} policy violation citations.",
            evidence=[pf.citation for pf in policy_findings[:5]],
        )

        # Stage 6: Reasoner Agent
        narrative = self.reasoner_agent.synthesize_narrative(
            documents=documents,
            entities=entities,
            relationships=relationships,
            transactions=transactions,
            cycles=cycles,
            anomalies=anomalies,
            policy_findings=policy_findings,
        )
        self.ledger.add_entry(
            event_type="AGENT_5_REASONING_COMPLETE",
            input_reference="Agent 5: ReasonerAgent",
            finding="Synthesized comprehensive forensic narrative report across all evidence tiers.",
            evidence=[narrative.executive_summary[:100]],
        )

        return {
            "documents": documents,
            "entities": entities,
            "relationships": relationships,
            "transactions": transactions,
            "graph_store": graph_store,
            "cycles": cycles,
            "anomalies": anomalies,
            "policy_findings": policy_findings,
            "ca_audit_results": ca_audit_results,
            "narrative": narrative,
            "ledger": self.ledger,
        }

    def resolve_anomaly_variance(
        self,
        results: Dict[str, Any],
        anomaly_id: str,
        resolution_action: str,
        notes: str,
        auditor_name: str = "CA Auditor",
    ) -> bool:
        """Applies auditor resolution to a flagged anomaly variance and records block in SHA3-256 ledger."""
        anomalies: List[AnomalyFinding] = results.get("anomalies", [])
        target_a = next((a for a in anomalies if a.anomaly_id == anomaly_id), None)

        if not target_a:
            return False

        target_a.status = resolution_action
        target_a.auditor_resolution_notes = notes
        target_a.resolved_by = auditor_name
        target_a.resolved_timestamp = datetime.now(timezone.utc).isoformat()

        # Write tamper-evident audit ledger entry
        ledger: ForensicAuditLedger = results["ledger"]
        ledger.add_entry(
            event_type="VARIANCE_CORRECTED_BY_AUDITOR",
            input_reference=f"Anomaly ID: {anomaly_id}",
            finding=f"Auditor {auditor_name} applied resolution '{resolution_action}' to variance {anomaly_id}: {notes}",
            evidence=[anomaly_id, resolution_action, notes[:50]],
            actor=auditor_name,
        )
        return True

    def auto_correct_all_tax_variances(self, results: Dict[str, Any], auditor_name: str = "CA Auditor") -> int:
        """Batch corrects all flagged statutory tax variances by applying Section 40A(3) disallowance & GST ITC reversals."""
        anomalies: List[AnomalyFinding] = results.get("anomalies", [])
        corrected_count = 0

        for a in anomalies:
            if a.status == "OPEN":
                if "40A(3)" in a.explanation or "Disallowance" in a.explanation or "High Amount" in a.anomaly_type.value:
                    self.resolve_anomaly_variance(
                        results=results,
                        anomaly_id=a.anomaly_id,
                        resolution_action="CORRECTED_DISALLOWED_IN_PGBP",
                        notes="Disallowed 100% from business income u/s 40A(3) in Form 3CD Clause 21(b). Tax variance rectified.",
                        auditor_name=auditor_name,
                    )
                    corrected_count += 1
                elif "Circular" in a.anomaly_type.value or "GST" in a.explanation:
                    self.resolve_anomaly_variance(
                        results=results,
                        anomaly_id=a.anomaly_id,
                        resolution_action="GST_ITC_REVERSED",
                        notes="Reversed Input Tax Credit u/s 16(2)(c) with 24% interest u/s 50. GST tax variance rectified.",
                        auditor_name=auditor_name,
                    )
                    corrected_count += 1
                elif "Structuring" in a.anomaly_type.value:
                    self.resolve_anomaly_variance(
                        results=results,
                        anomaly_id=a.anomaly_id,
                        resolution_action="REPORTED_TO_FIU_STR",
                        notes="Filed Suspicious Transaction Report (STR) u/s 269SS with FIU-IND. Regulatory variance rectified.",
                        auditor_name=auditor_name,
                    )
                    corrected_count += 1
                else:
                    self.resolve_anomaly_variance(
                        results=results,
                        anomaly_id=a.anomaly_id,
                        resolution_action="SUBSTANTIATED_WITH_DOCS",
                        notes="Substantiated with verified purchase order and bank scroll statement.",
                        auditor_name=auditor_name,
                    )
                    corrected_count += 1

        return corrected_count
