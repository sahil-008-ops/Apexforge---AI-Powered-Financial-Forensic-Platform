"""
Document Intelligence & Extraction Pipeline
Extracts structured financial entities, transactions, and relationships from heterogeneous document text.
Maintains exact provenance (document_id, snippet, confidence) for every finding.
"""

import re
import uuid
from typing import List, Tuple, Dict, Any
from apexforge.models.data_models import (
    NormalizedDocument,
    Entity,
    EntityType,
    Relationship,
    RelationType,
    Transaction,
)


class DocumentExtractor:
    def __init__(self):
        # Regex patterns for high-precision extraction
        self.iban_pattern = re.compile(r"\b([A-Z]{2}\d{2}[A-Z0-9]{11,30}|ACCT-\d{4,8}|ACC-\d{4,8}|\d{8,12})\b")
        self.amount_pattern = re.compile(r"\$?\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?)\s*(USD|EUR|GBP|USD)?\b")
        self.date_pattern = re.compile(r"\b(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4})\b")
        self.invoice_pattern = re.compile(r"\b(INV-\d{4}-\d{3,5}|Invoice\s*#?\s*\d+|INV#\d+)\b", re.IGNORECASE)
        self.email_pattern = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
        
        # Financial keywords for contextual relationship mining
        self.transfer_verbs = ["transferred", "wired", "paid", "sent", "remitted", "moved", "deposited", "credited"]
        self.invoice_verbs = ["invoiced", "billed", "charged", "issued invoice"]
        self.approval_verbs = ["approved", "authorized", "signed off", "cleared"]

    def extract_from_document(
        self, doc: NormalizedDocument
    ) -> Tuple[List[Entity], List[Relationship], List[Transaction]]:
        text = doc.extracted_text
        doc_id = doc.document_id
        
        entities: List[Entity] = []
        relationships: List[Relationship] = []
        transactions: List[Transaction] = []

        # Entity deduplication index per document
        entity_map: Dict[str, Entity] = {}

        def get_or_create_entity(name: str, etype: EntityType, evidence: str = "") -> Entity:
            key = f"{etype.value}:{name.strip().upper()}"
            if key in entity_map:
                return entity_map[key]
            
            ent_id = f"ENT-{uuid.uuid4().hex[:8].upper()}"
            ent = Entity(
                entity_id=ent_id,
                name=name.strip(),
                entity_type=etype,
                document_id=doc_id,
                evidence_text=evidence[:200],
                confidence=0.95,
            )
            entity_map[key] = ent
            entities.append(ent)
            return ent

        lines = text.splitlines()
        
        # 1. Structured CSV/Tabular Extraction
        if doc.document_type.value == "csv":
            self._extract_csv_rows(text, doc_id, get_or_create_entity, relationships, transactions)

        # 2. Extract Invoices, Accounts, Emails
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            # Invoice match
            inv_matches = self.invoice_pattern.findall(line_str)
            for inv in inv_matches:
                get_or_create_entity(inv, EntityType.INVOICE, line_str)

            # Account / IBAN match
            acct_matches = self.iban_pattern.findall(line_str)
            for acct in acct_matches:
                if len(acct) >= 6:
                    get_or_create_entity(acct, EntityType.ACCOUNT, line_str)

            # Email match
            email_matches = self.email_pattern.findall(line_str)
            for email in email_matches:
                get_or_create_entity(email, EntityType.EMAIL, line_str)

        # 3. Extract Explicit Entities & Transaction Narratives from text lines
        for line in lines:
            line_str = line.strip()

            # Pattern: COMPANY_A paid/transferred $AMOUNT to COMPANY_B [on DATE] [Ref: REF]
            # Pattern: From: ENTITY_A, To: ENTITY_B, Amount: $AMOUNT
            self._parse_transaction_sentence(
                line_str, doc_id, get_or_create_entity, relationships, transactions
            )
            self._parse_approval_sentence(
                line_str, doc_id, get_or_create_entity, relationships
            )

        # 4. Extract explicit metadata relationships (e.g. Email headers From/To)
        if "email_from" in doc.metadata and "email_to" in doc.metadata:
            sender = get_or_create_entity(doc.metadata["email_from"], EntityType.PERSON, "Email Header From")
            recv = get_or_create_entity(doc.metadata["email_to"], EntityType.PERSON, "Email Header To")
            rel = Relationship(
                relationship_id=f"REL-{uuid.uuid4().hex[:8].upper()}",
                source_id=sender.entity_id,
                target_id=recv.entity_id,
                relation_type=RelationType.CONNECTED_TO,
                document_id=doc_id,
                evidence_text=f"Email communication: {doc.metadata.get('email_subject', '')}",
            )
            relationships.append(rel)

        return entities, relationships, transactions

    def _parse_transaction_sentence(
        self,
        line: str,
        doc_id: str,
        get_or_create_entity,
        relationships: List[Relationship],
        transactions: List[Transaction],
    ):
        line_lower = line.lower()
        if any(verb in line_lower for verb in self.transfer_verbs):
            # Look for amounts
            amounts = self.amount_pattern.findall(line)
            # Look for dates
            dates = self.date_pattern.findall(line)
            date_str = dates[0] if dates else "2026-01-01"

            # Parse sender -> receiver using regex heuristics or delimiters
            # e.g., "Shell Corp Alpha transferred $45,000.00 to Vanguard Trading"
            m = re.search(r"([A-Za-z0-9\s&,.]+)\s+(?:wired|transferred|paid|sent|moved)\s+\$?([0-9,]+(?:\.[0-9]{2})?)\s*(?:USD|EUR|GBP)?\s+to\s+([A-Za-z0-9\s&,.]+)", line, re.IGNORECASE)
            if m:
                sender_name = m.group(1).strip()
                amount_val = float(m.group(2).replace(",", ""))
                receiver_name = m.group(3).strip()

                # Clean entity names
                sender_name = re.sub(r"^(From|On|Date|Ref):\s*", "", sender_name, flags=re.IGNORECASE).strip()
                receiver_name = re.sub(r"\s+(on|ref|via|dated|invoice).*", "", receiver_name, flags=re.IGNORECASE).strip()

                if len(sender_name) > 2 and len(receiver_name) > 2:
                    sender_ent = get_or_create_entity(sender_name, EntityType.COMPANY, line)
                    receiver_ent = get_or_create_entity(receiver_name, EntityType.COMPANY, line)

                    # Relationship
                    rel = Relationship(
                        relationship_id=f"REL-{uuid.uuid4().hex[:8].upper()}",
                        source_id=sender_ent.entity_id,
                        target_id=receiver_ent.entity_id,
                        relation_type=RelationType.PAID,
                        document_id=doc_id,
                        evidence_text=line,
                    )
                    relationships.append(rel)

                    # Transaction
                    tx_id = f"TX-{uuid.uuid4().hex[:8].upper()}"
                    tx = Transaction(
                        transaction_id=tx_id,
                        sender_id=sender_ent.entity_id,
                        sender_name=sender_ent.name,
                        receiver_id=receiver_ent.entity_id,
                        receiver_name=receiver_ent.name,
                        amount=amount_val,
                        currency="USD",
                        timestamp=date_str,
                        payment_reference=f"Ref in {doc_id}",
                        document_id=doc_id,
                        evidence_text=line,
                    )
                    transactions.append(tx)

    def _parse_approval_sentence(
        self,
        line: str,
        doc_id: str,
        get_or_create_entity,
        relationships: List[Relationship],
    ):
        m = re.search(r"([A-Za-z\s.]+)\s+(?:approved|authorized|signed off on)\s+(invoice|payment|transfer|INV-[0-9-]+)\s+(?:for\s+)?([A-Za-z0-9\s&,.]+)?", line, re.IGNORECASE)
        if m:
            approver_name = m.group(1).strip()
            target_item = m.group(2).strip()
            approver_ent = get_or_create_entity(approver_name, EntityType.PERSON, line)
            
            if "INV-" in line:
                inv_match = re.search(r"(INV-\d{4}-\d+)", line)
                if inv_match:
                    inv_ent = get_or_create_entity(inv_match.group(1), EntityType.INVOICE, line)
                    rel = Relationship(
                        relationship_id=f"REL-{uuid.uuid4().hex[:8].upper()}",
                        source_id=approver_ent.entity_id,
                        target_id=inv_ent.entity_id,
                        relation_type=RelationType.APPROVED,
                        document_id=doc_id,
                        evidence_text=line,
                    )
                    relationships.append(rel)

    def _extract_csv_rows(
        self,
        csv_text: str,
        doc_id: str,
        get_or_create_entity,
        relationships: List[Relationship],
        transactions: List[Transaction],
    ):
        lines = csv_text.splitlines()
        if not lines:
            return
        
        headers = [h.strip().lower() for h in lines[0].split(",")]
        
        # Identify columns
        sender_col = next((i for i, h in enumerate(headers) if "sender" in h or "from" in h or "source" in h), None)
        receiver_col = next((i for i, h in enumerate(headers) if "receiver" in h or "to" in h or "dest" in h or "target" in h), None)
        amount_col = next((i for i, h in enumerate(headers) if "amount" in h or "sum" in h or "val" in h), None)
        date_col = next((i for i, h in enumerate(headers) if "date" in h or "time" in h or "timestamp" in h), None)
        ref_col = next((i for i, h in enumerate(headers) if "ref" in h or "desc" in h or "id" in h), None)

        for line in lines[1:]:
            parts = [p.strip() for p in line.split(",")]
            if len(parts) <= max(filter(lambda x: x is not None, [sender_col, receiver_col, amount_col]), default=-1):
                continue
            
            try:
                s_name = parts[sender_col] if sender_col is not None else "Unknown Sender"
                r_name = parts[receiver_col] if receiver_col is not None else "Unknown Receiver"
                raw_amt = parts[amount_col] if amount_col is not None else "0"
                amt = float(re.sub(r"[^\d.]", "", raw_amt)) if raw_amt else 0.0
                dt = parts[date_col] if date_col is not None else "2026-01-01"
                ref = parts[ref_col] if ref_col is not None else ""

                if s_name and r_name and amt > 0:
                    s_ent = get_or_create_entity(s_name, EntityType.ACCOUNT if "ACCT" in s_name or "US" in s_name else EntityType.COMPANY, line)
                    r_ent = get_or_create_entity(r_name, EntityType.ACCOUNT if "ACCT" in r_name or "US" in r_name else EntityType.COMPANY, line)

                    rel = Relationship(
                        relationship_id=f"REL-{uuid.uuid4().hex[:8].upper()}",
                        source_id=s_ent.entity_id,
                        target_id=r_ent.entity_id,
                        relation_type=RelationType.TRANSFERRED_TO,
                        document_id=doc_id,
                        evidence_text=line,
                    )
                    relationships.append(rel)

                    tx = Transaction(
                        transaction_id=f"TX-{uuid.uuid4().hex[:8].upper()}",
                        sender_id=s_ent.entity_id,
                        sender_name=s_ent.name,
                        receiver_id=r_ent.entity_id,
                        receiver_name=r_ent.name,
                        amount=amt,
                        currency="USD",
                        timestamp=dt,
                        payment_reference=ref,
                        document_id=doc_id,
                        evidence_text=line,
                    )
                    transactions.append(tx)
            except Exception:
                continue
