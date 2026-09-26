import pytest
from apexforge.generator.synthetic_data import SyntheticDataGenerator
from apexforge.agents.orchestrator import ForensicOrchestrator


def test_full_pipeline_multiagent_benchmark():
    generator = SyntheticDataGenerator(seed=42)
    documents = generator.generate_benchmark_dataset()

    assert len(documents) >= 50

    orchestrator = ForensicOrchestrator()
    results = orchestrator.run_investigation_pipeline(documents)

    assert "documents" in results
    assert "entities" in results
    assert "transactions" in results
    assert "cycles" in results
    assert "anomalies" in results
    assert "policy_findings" in results
    assert "narrative" in results
    assert "ledger" in results

    # Verify findings
    assert len(results["entities"]) > 0
    assert len(results["transactions"]) > 0
    assert len(results["cycles"]) > 0
    assert len(results["anomalies"]) > 0

    # Ledger integrity
    is_valid, count, _, msg = results["ledger"].verify_chain_integrity()
    assert is_valid is True
    assert count >= 6
