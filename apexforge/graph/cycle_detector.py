"""
Circular Transaction Detection Engine
Scans entity-transaction graphs to detect cyclic money flow patterns (A -> B -> C -> A)
and produces detailed, explainable evidence reports.
"""

import networkx as nx
import uuid
from typing import List, Dict, Any
from apexforge.graph.graph_store import TransactionGraphStore
from apexforge.models.data_models import TransactionCycle, Transaction


class CycleDetector:
    def __init__(self, graph_store: TransactionGraphStore):
        self.graph_store = graph_store

    def detect_circular_transactions(self, min_length: int = 2, max_length: int = 6) -> List[TransactionCycle]:
        """Detects simple cycles in the payment graph within specified length bounds."""
        g = self.graph_store.graph
        
        # Build payment-only directed graph for pure financial entity flow
        payment_graph = nx.DiGraph()
        
        for u, v, data in g.edges(data=True):
            rel_type = data.get("relation_type", "")
            if rel_type in ["PAID", "TRANSFERRED_TO"]:
                # If connecting entity -> transaction -> entity, resolve to direct entity connection
                node_u_type = g.nodes[u].get("node_type", "")
                node_v_type = g.nodes[v].get("node_type", "")
                
                # Exclude document nodes from cycle path
                if node_u_type != "Document" and node_v_type != "Document":
                    amt = data.get("amount", 0.0)
                    dt = data.get("timestamp", "")
                    doc_id = data.get("document_id", "")
                    tx_id = data.get("transaction_id", "")
                    ev = data.get("evidence", "")

                    payment_graph.add_edge(
                        u, v,
                        amount=amt,
                        timestamp=dt,
                        document_id=doc_id,
                        transaction_id=tx_id,
                        evidence=ev
                    )

        detected_cycles: List[TransactionCycle] = []
        seen_cycle_keys = set()

        try:
            # Find all simple cycles
            raw_cycles = list(nx.simple_cycles(payment_graph))
            
            for raw_cycle in raw_cycles:
                cycle_len = len(raw_cycle)
                if min_length <= cycle_len <= max_length:
                    # Normalize cycle representation for deduplication
                    # e.g., min element rotated to front
                    min_idx = raw_cycle.index(min(raw_cycle))
                    norm_cycle = tuple(raw_cycle[min_idx:] + raw_cycle[:min_idx])
                    
                    if norm_cycle in seen_cycle_keys:
                        continue
                    seen_cycle_keys.add(norm_cycle)

                    # Gather detailed edge metadata
                    entities_involved = []
                    transactions_involved = []
                    timestamps = []
                    source_docs = set()
                    evidence_list = []
                    total_amount = 0.0

                    # Resolve human labels for entities
                    for node in raw_cycle:
                        lbl = g.nodes[node].get("label", node)
                        entities_involved.append(f"{lbl} ({node})")

                    # Loop through cycle edges
                    for i in range(cycle_len):
                        u_node = raw_cycle[i]
                        v_node = raw_cycle[(i + 1) % cycle_len]
                        edge_data = payment_graph.get_edge_data(u_node, v_node) or {}
                        
                        amt = edge_data.get("amount", 0.0)
                        dt = edge_data.get("timestamp", "")
                        doc_id = edge_data.get("document_id", "")
                        tx_id = edge_data.get("transaction_id", "")
                        ev = edge_data.get("evidence", "")

                        total_amount += amt
                        if tx_id:
                            transactions_involved.append(tx_id)
                        if dt:
                            timestamps.append(dt)
                        if doc_id:
                            source_docs.add(doc_id)
                        if ev:
                            evidence_list.append(ev)

                    cycle_id = f"CYCLE-{uuid.uuid4().hex[:8].upper()}"
                    cycle_obj = TransactionCycle(
                        cycle_id=cycle_id,
                        entities_involved=entities_involved,
                        transactions_involved=transactions_involved,
                        total_amount=round(total_amount, 2),
                        timestamps=timestamps,
                        cycle_length=cycle_len,
                        source_documents=list(source_docs),
                        evidence=evidence_list,
                        risk_level="Anomalous Circular Payment Flow — Requires Forensic Verification",
                        explanation=(
                            f"Detected a {cycle_len}-step closed transaction loop totaling ${total_amount:,.2f}. "
                            f"Funds originate from and return to the same entity cluster ({entities_involved[0]} -> ... -> {entities_involved[-1]}). "
                            "This pattern is indicative of potential circular routing or pass-through transaction schemes."
                        ),
                    )
                    detected_cycles.append(cycle_obj)

        except Exception as e:
            print(f"[Cycle Detection Engine Warning]: Error discovering cycles: {e}")

        return detected_cycles
