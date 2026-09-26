"""
Agent 1 — Document / Extraction Agent
Inspects raw documents, extracts structured entities and transactions, normalizes dates and amounts.
"""

from typing import List, Tuple
from apexforge.ingestion.document_loader import DocumentLoader
from apexforge.intelligence.extraction import DocumentExtractor
from apexforge.models.data_models import (
    NormalizedDocument,
    Entity,
    Relationship,
    Transaction,
)


class ExtractionAgent:
    def __init__(self):
        self.extractor = DocumentExtractor()

    def process_documents(
        self, documents: List[NormalizedDocument]
    ) -> Tuple[List[Entity], List[Relationship], List[Transaction]]:
        all_entities: List[Entity] = []
        all_relationships: List[Relationship] = []
        all_transactions: List[Transaction] = []

        for doc in documents:
            ents, rels, txs = self.extractor.extract_from_document(doc)
            all_entities.extend(ents)
            all_relationships.extend(rels)
            all_transactions.extend(txs)

        return all_entities, all_relationships, all_transactions
