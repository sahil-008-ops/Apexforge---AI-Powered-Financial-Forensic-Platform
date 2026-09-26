import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    
    from apexforge.generator.synthetic_data import SyntheticDataGenerator
    from apexforge.agents.orchestrator import ForensicOrchestrator

    print("=== 1. SYSTEM INITIALIZATION CHECK ===")
    gen = SyntheticDataGenerator(seed=42)
    docs = gen.generate_benchmark_dataset()
    print(f"Ingested Benchmark Documents: {len(docs)}")

    print("\n=== 2. MULTI-AGENT PIPELINE EXECUTION ===")
    orch = ForensicOrchestrator()
    results = orch.run_investigation_pipeline(docs)

    print(f"Extracted Entities: {len(results['entities'])}")
    print(f"Extracted Transactions: {len(results['transactions'])}")
    print(f"Detected Circular Payment Loops: {len(results['cycles'])}")
    print(f"Detected Anomaly Findings: {len(results['anomalies'])}")
    print(f"Policy Violation Citations: {len(results['policy_findings'])}")

    ca_results = results['ca_audit_results']
    metrics = ca_results['summary_metrics']
    
    print("\n=== 3. FLAGGED STATUTORY TAX & COMPLIANCE VARIATIONS ===")
    print(f"Sec 40A(3) Cash Disallowance [Clause 21(b)]: ₹{metrics['total_sec_40a3_disallowance']:,.2f} INR")
    print(f"Sec 269SS/269T Cash Loan Risk [Clause 31(a)/(b)]: ₹{metrics['total_sec_269ss_penalty_exposure']:,.2f} INR")
    print(f"CGST Sec 16(2)/132 Circular ITC at Risk: ₹{metrics['total_gst_circular_itc_at_risk']:,.2f} INR")
    print(f"Total Flagged Statutory Audit Variations: {metrics['total_flagged_tax_items']}")

    print("\n=== 4. ANOMALY SEVERITY BREAKDOWN ===")
    anomalies = results['anomalies']
    sev_counts = {}
    for a in anomalies:
        sev_counts[a.severity.value] = sev_counts.get(a.severity.value, 0) + 1
    for k, v in sev_counts.items():
        print(f" - {k} Severity: {v} findings")

    print("\n=== 5. TOP FLAGGED VARIATIONS & DEVIATION POINTERS ===")
    for idx, a in enumerate(anomalies[:5], 1):
        print(f"\n[Variation #{idx}] Category: {a.anomaly_type.value} ({a.severity.value})")
        print(f"  Explanation: {a.explanation}")
        print(f"  Target Baseline: {a.expected_baseline}")
        print(f"  Observed Value:  {a.observed_value}")
        print(f"  Deviation Delta: {a.deviation_delta}")
        print(f"  Evidence Pointer: {a.evidence_location}")

    is_valid, count, _, msg = results['ledger'].verify_chain_integrity()
    print("\n=== 6. CRYPTOGRAPHIC LEDGER INTEGRITY ===")
    print(f"Chain Status: {'VERIFIED' if is_valid else 'FAILED'} ({count} SHA3-256 blocks)")

if __name__ == "__main__":
    main()
