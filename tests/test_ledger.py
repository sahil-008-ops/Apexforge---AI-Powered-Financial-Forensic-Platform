import pytest
from apexforge.ledger.audit_ledger import ForensicAuditLedger


def test_audit_ledger_integrity():
    ledger = ForensicAuditLedger()

    entry1 = ledger.add_entry("INIT", "DOC-001", "Pipeline started", ["hash1"])
    entry2 = ledger.add_entry("EXTRACTION", "DOC-001", "Extracted 5 entities", ["ent1", "ent2"])

    is_valid, count, tampered_idx, msg = ledger.verify_chain_integrity()
    assert is_valid is True
    assert count == 2
    assert tampered_idx is None

    # Demonstrate Tamper Evidence Detection
    ledger.chain[0].finding = "TAMPERED DATA"
    is_valid, count, tampered_idx, msg = ledger.verify_chain_integrity()
    assert is_valid is False
    assert tampered_idx == 0
    assert "TAMPER DETECTED" in msg
