"""
Multi-Agent Orchestrator Engine
Coordinates the execution state-machine across all 5 agents (Extraction, Linker, Anomaly, Policy, Reasoner)
and writes tamper-evident SHA3-256 audit ledger entries at each state transition.
"""

from typing import List, Dict, Any
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

    def run_investigation_pipeline(self, documents: List[NormalizedDocument]) -> Dict[str, Any]:
        """Runs full multi-agent investigation workflow over ingested documents."""
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

        # Stage 4: Policy / Verification Agent
        policy_findings = self.policy_agent.verify_anomalies_against_policies(anomalies)
        self.ledger.add_entry(
            event_type="AGENT_4_POLICY_VERIFICATION_COMPLETE",
            input_reference="Agent 4: PolicyAgent",
            finding=f"Matched findings against policy vector store, issuing {len(policy_findings)} policy violation citations.",
            evidence=[pf.citation for pf in policy_findings[:5]],
        )

        # Stage 5: Reasoner Agent
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
            "narrative": narrative,
            "ledger": self.ledger,
        }
