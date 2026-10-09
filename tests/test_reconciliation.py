import pytest
from apexforge.models.data_models import Transaction, ReconciliationMatchStatus
from apexforge.ledger_generation.auto_ledger import AutoLedgerGenerator
from apexforge.reconciliation.bank_reconciliation import BankReconciliationEngine
from apexforge.reconciliation.ais_reconciliation import AISReconciliationEngine
from apexforge.reconciliation.unified_reconciliation import UnifiedReconciliationEngine


def test_bank_reconciliation():
    bank_txs = [
        Transaction(
            transaction_id="TX-201",
            sender_id="BANK-1",
            sender_name="HDFC Bank",
            receiver_id="ENT-1",
            receiver_name="Vanguard Goods",
            amount=500000.0,
            currency="INR",
            timestamp="2024-05-01T10:00:00Z",
            payment_reference="NEFT / Vanguard Purchase",
        ),
        Transaction(
            transaction_id="TX-202",
            sender_id="BANK-1",
            sender_name="HDFC Bank",
            receiver_id="ENT-2",
            receiver_name="Bank Fee",
            amount=250.0,
            currency="INR",
            timestamp="2024-05-02T11:00:00Z",
            payment_reference="Monthly Ledger Maintenance Fee / GST Chg",
        ),
    ]

    generator = AutoLedgerGenerator()
    ledger_entries = generator.generate_ledger_entries(bank_txs)

    engine = BankReconciliationEngine()
    lines = engine.reconcile(bank_txs, ledger_entries)
    assert len(lines) >= 2

    summary = engine.get_reconciliation_summary()
    assert summary["total_line_items"] >= 2


def test_ais_reconciliation():
    txs = [
        Transaction(
            transaction_id="TX-301",
            sender_id="ENT-1",
            sender_name="Apex Corp",
            receiver_id="ENT-2",
            receiver_name="Vanguard Goods",
            amount=13500000.0,
            currency="INR",
            timestamp="2024-05-10T10:00:00Z",
            payment_reference="Contract Payment",
        )
    ]
    generator = AutoLedgerGenerator()
    ledger_entries = generator.generate_ledger_entries(txs)

    ais_engine = AISReconciliationEngine()
    ais_records = ais_engine.reconcile_with_books(ledger_entries, txs)
    assert len(ais_records) >= 3

    summary = ais_engine.get_ais_summary()
    assert summary["total_ais_records"] >= 3
    assert summary["unreported_income_variance_inr"] > 0


def test_unified_reconciliation():
    txs = [
        Transaction(
            transaction_id="TX-401",
            sender_id="ENT-1",
            sender_name="Apex Corp",
            receiver_id="ENT-2",
            receiver_name="Shell Co India",
            amount=13500000.0,
            currency="INR",
            timestamp="2024-05-15T10:00:00Z",
            payment_reference="Pass-through Transfer",
            document_id="DOC-CSV-001",
        )
    ]
    generator = AutoLedgerGenerator()
    ledger_entries = generator.generate_ledger_entries(txs)

    bank_engine = BankReconciliationEngine()
    bank_lines = bank_engine.reconcile(txs, ledger_entries)

    ais_engine = AISReconciliationEngine()
    ais_records = ais_engine.reconcile_with_books(ledger_entries, txs)

    unified_engine = UnifiedReconciliationEngine()
    matrix = unified_engine.build_unified_matrix(
        transactions=txs,
        ledger_entries=ledger_entries,
        bank_lines=bank_lines,
        ais_records=ais_records,
        cycles=[],
    )
    assert len(matrix) == 1
    summary = unified_engine.get_unified_summary()
    assert summary["total_matrix_entries"] == 1
