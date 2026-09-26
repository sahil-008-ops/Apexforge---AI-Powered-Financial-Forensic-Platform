"""
Graph Database Layer (Neo4j + NetworkX Dual Engine)
Provides entity-transaction graph management, path tracing, sub-graph extraction, and query utilities.
"""

import networkx as nx
from typing import List, Dict, Any, Optional, Set, Tuple
from apexforge.models.data_models import Entity, Relationship, Transaction, NormalizedDocument


class TransactionGraphStore:
    def __init__(self, use_neo4j: bool = False, neo4j_uri: str = None, neo4j_user: str = None, neo4j_password: str = None):
        self.graph = nx.DiGraph()
        self.use_neo4j = use_neo4j
        self.neo4j_driver = None

        if use_neo4j:
            try:
                from neo4j import GraphDatabase
                self.neo4j_driver = GraphDatabase.driver(
                    neo4j_uri or "bolt://localhost:7687",
                    auth=(neo4j_user or "neo4j", neo4j_password or "password"),
                )
            except Exception as e:
                print(f"[Neo4j Driver Info]: Neo4j not available ({e}). Defaulting to NetworkX in-memory graph engine.")
                self.use_neo4j = False

    def add_document_node(self, doc: NormalizedDocument):
        self.graph.add_node(
            doc.document_id,
            node_type="Document",
            label=doc.filename,
            document_type=doc.document_type.value,
            sha3_hash=doc.sha3_256_hash,
        )

    def add_entity_node(self, entity: Entity):
        self.graph.add_node(
            entity.entity_id,
            node_type=entity.entity_type.value,
            label=entity.name,
            document_id=entity.document_id,
            confidence=entity.confidence,
        )
        if entity.document_id and self.graph.has_node(entity.document_id):
            self.graph.add_edge(
                entity.entity_id,
                entity.document_id,
                relation_type="REFERENCED_IN",
                document_id=entity.document_id,
                evidence=entity.evidence_text,
            )

    def add_relationship_edge(self, rel: Relationship):
        self.graph.add_edge(
            rel.source_id,
            rel.target_id,
            relationship_id=rel.relationship_id,
            relation_type=rel.relation_type.value,
            document_id=rel.document_id,
            evidence=rel.evidence_text,
        )

    def add_transaction(self, tx: Transaction):
        # Create transaction node or direct directed edge between entities
        tx_node_id = tx.transaction_id
        self.graph.add_node(
            tx_node_id,
            node_type="Transaction",
            label=f"${tx.amount:,.2f}",
            amount=tx.amount,
            timestamp=tx.timestamp,
            currency=tx.currency,
            document_id=tx.document_id,
            evidence=tx.evidence_text,
        )

        # Connect sender -> tx_node -> receiver
        self.graph.add_edge(
            tx.sender_id,
            tx_node_id,
            relation_type="TRANSFERRED_TO",
            amount=tx.amount,
            timestamp=tx.timestamp,
            document_id=tx.document_id,
        )
        self.graph.add_edge(
            tx_node_id,
            tx.receiver_id,
            relation_type="RECEIVED",
            amount=tx.amount,
            timestamp=tx.timestamp,
            document_id=tx.document_id,
        )

        # Also add direct payment edge for path finding
        self.graph.add_edge(
            tx.sender_id,
            tx.receiver_id,
            relation_type="PAID",
            amount=tx.amount,
            timestamp=tx.timestamp,
            transaction_id=tx.transaction_id,
            document_id=tx.document_id,
            evidence=tx.evidence_text,
        )

    def build_graph_from_extracted_data(
        self,
        docs: List[NormalizedDocument],
        entities: List[Entity],
        relationships: List[Relationship],
        transactions: List[Transaction],
    ):
        for doc in docs:
            self.add_document_node(doc)
        for ent in entities:
            self.add_entity_node(ent)
        for rel in relationships:
            self.add_relationship_edge(rel)
        for tx in transactions:
            self.add_transaction(tx)

    def trace_transaction_path(self, source_id: str, target_id: str) -> List[List[str]]:
        """Finds all simple paths between source and target entities."""
        if not self.graph.has_node(source_id) or not self.graph.has_node(target_id):
            return []
        try:
            paths = list(nx.all_simple_paths(self.graph, source=source_id, target=target_id, cutoff=6))
            return paths
        except Exception:
            return []

    def get_entity_neighbors(self, entity_id: str) -> Dict[str, Any]:
        """Returns direct counter-parties and connected entities."""
        if not self.graph.has_node(entity_id):
            return {}
        
        predecessors = list(self.graph.predecessors(entity_id))
        successors = list(self.graph.successors(entity_id))

        return {
            "entity_id": entity_id,
            "incoming_edges": [
                {
                    "from": p,
                    "from_label": self.graph.nodes[p].get("label", p),
                    "data": self.graph.get_edge_data(p, entity_id),
                }
                for p in predecessors
            ],
            "outgoing_edges": [
                {
                    "to": s,
                    "to_label": self.graph.nodes[s].get("label", s),
                    "data": self.graph.get_edge_data(entity_id, s),
                }
                for s in successors
            ],
        }

    def get_graph_summary(self) -> Dict[str, Any]:
        node_counts = {}
        for n, d in self.graph.nodes(data=True):
            ntype = d.get("node_type", "Unknown")
            node_counts[ntype] = node_counts.get(ntype, 0) + 1

        rel_counts = {}
        for u, v, d in self.graph.edges(data=True):
            rtype = d.get("relation_type", "CONNECTED")
            rel_counts[rtype] = rel_counts.get(rtype, 0) + 1

        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "nodes_by_type": node_counts,
            "edges_by_type": rel_counts,
        }
