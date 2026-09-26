import pytest
from apexforge.ca_audit.ca_tax_engine import IndianCATaxAuditEngine
from apexforge.models.data_models import Transaction, Entity, EntityType, TransactionCycle


def test_indian_ca_tax_audit_engine():
    engine = IndianCATaxAuditEngine()

    # Cash transaction > 20,000 (Sec 269SS violation)
    tx1 = Transaction(
        transaction_id="TX-CASH-1",
        sender_id="E1",
        sender_name="John Doe",
        receiver_id="E2",
        receiver_name="Vendor Corp",
        amount=45000.0,
        currency="INR",
        timestamp="2026-03-01",
        payment_reference="Cash Deposit Tranche",
        evidence_text="Cash payment made in hand",
    )

    # Cash transaction > 10,000 for vendor expense (Sec 40A(3) disallowance)
    tx2 = Transaction(
        transaction_id="TX-CASH-2",
        sender_id="E1",
        sender_name="Client Corp",
        receiver_id="E3",
        receiver_name="Supplier Private Ltd",
        amount=15000.0,
        currency="INR",
        timestamp="2026-03-02",
        payment_reference="Vendor Cash Expense",
        evidence_text="Vendor invoice paid in cash currency",
    )

    cycle = TransactionCycle(
        cycle_id="CYC-GST-1",
        entities_involved=["Party A", "Party B", "Party C", "Party A"],
        transactions_involved=["TX-1", "TX-2", "TX-3"],
        total_amount=120000.0,
        timestamps=["2026-03-01", "2026-03-02", "2026-03-03"],
        cycle_length=3,
        source_documents=["DOC-1"],
        evidence=["Circular trading detected"],
        explanation="Circular loop",
    )

    results = engine.evaluate_indian_tax_compliance([tx1, tx2], [], [], [cycle])

    assert len(results["all_tax_findings"]) >= 3
    assert results["summary_metrics"]["total_sec_40a3_disallowance"] == 15000.0
    assert results["summary_metrics"]["total_sec_269ss_penalty_exposure"] == 45000.0
    assert results["summary_metrics"]["total_gst_circular_itc_at_risk"] == 120000.0

    # Test working paper markdown generation
    wp_md = engine.generate_ca_working_paper_md(results, "Test Assessee", "AY 2026-27")
    assert "Section 40A(3)" in wp_md
    assert "Section 269SS" in wp_md
    assert "Form 3CD" in wp_md
