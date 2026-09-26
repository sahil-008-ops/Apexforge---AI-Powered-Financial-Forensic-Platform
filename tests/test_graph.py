import pytest
from apexforge.graph.graph_store import TransactionGraphStore
from apexforge.graph.cycle_detector import CycleDetector
from apexforge.models.data_models import Entity, EntityType, Transaction


def test_graph_store_nodes_and_edges():
    store = TransactionGraphStore()
    e1 = Entity(entity_id="ENT-1", name="Alpha Corp", entity_type=EntityType.COMPANY, document_id="DOC-1")
    e2 = Entity(entity_id="ENT-2", name="Beta Corp", entity_type=EntityType.COMPANY, document_id="DOC-1")
    tx = Transaction(
        transaction_id="TX-100",
        sender_id="ENT-1",
        sender_name="Alpha Corp",
        receiver_id="ENT-2",
        receiver_name="Beta Corp",
        amount=50000.0,
        timestamp="2026-03-01",
        document_id="DOC-1",
    )

    store.add_entity_node(e1)
    store.add_entity_node(e2)
    store.add_transaction(tx)

    summary = store.get_graph_summary()
    assert summary["total_nodes"] >= 3
    paths = store.trace_transaction_path("ENT-1", "ENT-2")
    assert len(paths) > 0


def test_circular_transaction_detection():
    store = TransactionGraphStore()
    e1 = Entity(entity_id="E1", name="Entity A", entity_type=EntityType.COMPANY, document_id="D1")
    e2 = Entity(entity_id="E2", name="Entity B", entity_type=EntityType.COMPANY, document_id="D1")
    e3 = Entity(entity_id="E3", name="Entity C", entity_type=EntityType.COMPANY, document_id="D1")

    tx1 = Transaction(transaction_id="T1", sender_id="E1", sender_name="Entity A", receiver_id="E2", receiver_name="Entity B", amount=10000, timestamp="2026-03-01", document_id="D1")
    tx2 = Transaction(transaction_id="T2", sender_id="E2", sender_name="Entity B", receiver_id="E3", receiver_name="Entity C", amount=10000, timestamp="2026-03-02", document_id="D1")
    tx3 = Transaction(transaction_id="T3", sender_id="E3", sender_name="Entity C", receiver_id="E1", receiver_name="Entity A", amount=10000, timestamp="2026-03-03", document_id="D1")

    for e in [e1, e2, e3]:
        store.add_entity_node(e)
    for t in [tx1, tx2, tx3]:
        store.add_transaction(t)

    detector = CycleDetector(store)
    cycles = detector.detect_circular_transactions()

    assert len(cycles) == 1
    assert cycles[0].cycle_length == 3
    assert cycles[0].total_amount == 30000.0
