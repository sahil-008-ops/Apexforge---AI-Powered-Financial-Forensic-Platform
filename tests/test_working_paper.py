import pytest
from apexforge.models.data_models import AnomalyFinding, AnomalyCategory, AnomalySeverity, AuditReviewStatus
from apexforge.ledger.audit_ledger import ForensicAuditLedger
from apexforge.ca_audit.paper_generator import CAReviewWorkflow, AuditWorkingPaperGenerator


def test_ca_review_workflow_and_working_papers():
    ledger = ForensicAuditLedger()
    workflow = CAReviewWorkflow(ledger=ledger)
    paper_gen = AuditWorkingPaperGenerator(ledger=ledger)

    anomaly = AnomalyFinding(
        anomaly_id="ANO-TEST-01",
        anomaly_type=AnomalyCategory.CIRCULAR_TRANSACTION,
        anomaly_score=0.98,
        severity=AnomalySeverity.CRITICAL,
        explanation="Circular round-trip loop detected.",
        expected_baseline="Linear supply chain",
        observed_value="Closed loop path",
        evidence_location="DOC-CSV-001",
    )

    reviewed = workflow.review_anomaly(
        anomaly=anomaly,
        new_status=AuditReviewStatus.ACCEPTED,
        auditor_notes="Disallowed ITC u/s 16(2)",
    )
    assert reviewed.status == AuditReviewStatus.ACCEPTED
    assert len(ledger.event_chain) == 1

    paper = paper_gen.generate_working_paper([anomaly])
    assert paper.entity_name == "Apex Global Corp India Pvt Ltd"
    assert len(paper.schedules) == 3
    assert "SHA3-256" in paper.tamper_hash_chain_status

    md_report = paper_gen.export_working_paper_markdown(paper)
    assert "# 📜 ICAI STATUTORY AUDIT WORKING PAPER" in md_report
    assert "Form 3CD Clause 21(b)" in md_report
