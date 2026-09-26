"""
Agent 2 — Linker / Pattern Agent
Resolves duplicate entities, builds the unified transaction graph, and discovers multi-step transaction chains.
"""

from typing import List, Dict, Tuple
from apexforge.models.data_models import Entity, Relationship, Transaction, NormalizedDocument
from apexforge.graph.graph_store import TransactionGraphStore


class LinkerAgent:
    def __init__(self, graph_store: TransactionGraphStore):
        self.graph_store = graph_store

    def link_entities_and_build_graph(
        self,
        documents: List[NormalizedDocument],
        entities: List[Entity],
        relationships: List[Relationship],
        transactions: List[Transaction],
    ) -> TransactionGraphStore:
        # 1. Fuzzy Entity Resolution Index
        canonical_map: Dict[str, str] = {}
        
        for ent in entities:
            norm_name = ent.name.strip().upper()
            # Simple entity normalization (e.g., stripping LLC, Inc, Corp for matching)
            clean_name = norm_name.replace(" INC", "").replace(" LLC", "").replace(" CORP", "").replace(" LTD", "")
            canonical_map[ent.entity_id] = clean_name

        # 2. Build Transaction Graph
        self.graph_store.build_graph_from_extracted_data(
            docs=documents,
            entities=entities,
            relationships=relationships,
            transactions=transactions,
        )

        return self.graph_store
