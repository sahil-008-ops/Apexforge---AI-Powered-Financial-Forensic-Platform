"""
Agent 5 — Reasoner Agent
Synthesizes findings from extraction, linker, anomaly, and policy agents into a structured forensic narrative.
Categorizes evidence into Observed Facts, Derived Relationships, Anomalies, Hypotheses, Policy Violations, and Unresolved Questions.
Uses Indian Rupee (₹ INR) financial reporting standard.
"""

from typing import List
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


class ReasonerAgent:
    def __init__(self):
        pass

    def synthesize_narrative(
        self,
        documents: List[NormalizedDocument],
        entities: List[Entity],
        relationships: List[Relationship],
        transactions: List[Transaction],
        cycles: List[TransactionCycle],
        anomalies: List[AnomalyFinding],
        policy_findings: List[PolicyFinding],
    ) -> ForensicNarrativeSection:
        observed_facts: List[str] = []
        derived_relationships: List[str] = []
        anomaly_list: List[str] = []
        hypotheses: List[str] = []
        policy_violations: List[str] = []
        unresolved_questions: List[str] = []

        # 1. Observed Facts (Direct Evidence in ₹ INR)
        observed_facts.append(f"Ingested and analyzed {len(documents)} financial evidence documents with SHA3-256 integrity provenance.")
        total_volume = sum(t.amount for t in transactions)
        observed_facts.append(f"Recorded {len(transactions)} transactions totaling ₹{total_volume:,.2f} INR across {len(entities)} extracted entities.")
        for tx in transactions[:5]:
            observed_facts.append(f"Fact: Transfer of ₹{tx.amount:,.2f} from '{tx.sender_name}' to '{tx.receiver_name}' on {tx.timestamp} (Doc: {tx.document_id}).")

        # 2. Derived Relationships (Inferred Links)
        for rel in relationships[:10]:
            src_name = rel.source_id
            tgt_name = rel.target_id
            derived_relationships.append(f"Derived: {src_name} --[{rel.relation_type.value}]--> {tgt_name} (Doc: {rel.document_id}).")

        # 3. Anomalies
        for ano in anomalies:
            anomaly_list.append(f"[{ano.severity.value} | Score: {ano.anomaly_score:.2f}] {ano.anomaly_type.value}: {ano.explanation}")

        # 4. Policy Violations (Statutory Indian Laws & Internal Controls)
        seen_citations = set()
        for pf in policy_findings:
            if pf.citation not in seen_citations:
                seen_citations.add(pf.citation)
                policy_violations.append(f"Violation of {pf.policy_title} ({pf.policy_section}): {pf.description}")

        # 5. Hypotheses (Forensic Inferences for CA Audit Review)
        if cycles:
            hypotheses.append(
                f"Hypothesis: Identified {len(cycles)} circular payment paths totaling ₹{sum(c.total_amount for c in cycles):,.2f} INR. "
                "These loops indicate potential GST round-tripping or artificial turnover inflation schemes between shell entities."
            )
        structuring_anomalies = [a for a in anomalies if "Structuring" in a.anomaly_type.value]
        if structuring_anomalies:
            hypotheses.append(
                "Hypothesis: Multiple cash transfer amounts immediately below statutory reporting limits suggest intentional smurfing/structuring."
            )

        # 6. Unresolved Questions
        if any("MISSING_DOCUMENTATION" in a.anomaly_type.name for a in anomalies):
            unresolved_questions.append("Unresolved: Lack of matching invoices/POs for high-value transfers requires bank statement sub-poenas and e-way bill verification.")
        unresolved_questions.append("Unresolved: Ultimate beneficial ownership (UBO) for offshore intermediary shell entities requires MCA / RoC registry lookup.")

        # Executive Summary
        exec_summary = (
            f"ApexForge Multi-Agent Forensic CA Investigation completed analysis of {len(documents)} evidence files. "
            f"Extracted {len(entities)} entities and {len(transactions)} transactions totaling ₹{total_volume:,.2f} INR. "
            f"Discovered {len(cycles)} circular transaction loops and {len(anomalies)} anomalies "
            f"({len([a for a in anomalies if a.severity.value == 'CRITICAL'])} Critical). "
            f"Cross-verified {len(seen_citations)} statutory Indian tax laws & internal policy control violations."
        )

        return ForensicNarrativeSection(
            executive_summary=exec_summary,
            observed_facts=observed_facts,
            derived_relationships=derived_relationships,
            anomalies=anomaly_list,
            hypotheses=hypotheses,
            policy_violations=policy_violations,
            unresolved_questions=unresolved_questions,
        )
