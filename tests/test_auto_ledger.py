import pytest
from apexforge.models.data_models import Transaction, LedgerCategory, AuditReviewStatus
from apexforge.ledger_generation.auto_ledger import AutoLedgerGenerator


def test_auto_ledger_classification():
    generator = AutoLedgerGenerator()
    txs = [
        Transaction(
            transaction_id="TX-101",
            sender_id="ENT-1",
            sender_name="Horizon Holdings",
            receiver_id="ENT-2",
            receiver_name="Legal Firm & Co",
            amount=150000.0,
            currency="INR",
            timestamp="2024-04-10T10:00:00Z",
            payment_reference="Professional Fees & Legal Consulting",
        ),
        Transaction(
            transaction_id="TX-102",
            sender_id="ENT-2",
            sender_name="Apex Corp",
            receiver_id="ENT-3",
            receiver_name="Vanguard Goods",
            amount=6000000.0,
            currency="INR",
            timestamp="2024-04-12T14:30:00Z",
            payment_reference="Raw Material Purchase Invoice",
        ),
    ]

    entries = generator.generate_ledger_entries(txs)
    assert len(entries) == 2
    assert entries[0].category == LedgerCategory.INDIRECT_EXPENSE
    assert "Sec 194J" in entries[0].tds_section
    assert entries[1].category == LedgerCategory.PURCHASE_EXPENSE
    assert "Sec 194Q" in entries[1].tds_section


def test_ca_review_workflow():
    generator = AutoLedgerGenerator()
    tx = Transaction(
        transaction_id="TX-103",
        sender_id="ENT-1",
        sender_name="Apex Corp",
        receiver_id="ENT-2",
        receiver_name="ABC Suppliers",
        amount=50000.0,
        currency="INR",
        timestamp="2024-04-15T12:00:00Z",
        payment_reference="General Expense",
    )
    entries = generator.generate_ledger_entries([tx])
    entry = entries[0]
    
    reviewed = generator.ca_review_entry(entry.entry_id, AuditReviewStatus.ACCEPTED, "Verified invoice")
    assert reviewed is not None
    assert reviewed.status == AuditReviewStatus.ACCEPTED
    assert reviewed.ca_notes == "Verified invoice"
