"""
ApexForge Data Models
Core Pydantic data structures for internal document representation, extracted entities,
transactions, graph cycles, anomalies, policy findings, and ledger entries.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class DocumentType(str, Enum):
    PDF = "pdf"
    IMAGE = "image"
    CSV = "csv"
    TXT = "txt"
    EMAIL = "email"
    CHAT = "chat"


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSED = "processed"
    FAILED = "failed"


class EntityType(str, Enum):
    PERSON = "Person"
    ORGANIZATION = "Organization"
    COMPANY = "Company"
    BANK = "Bank"
    ACCOUNT = "Account"
    TRANSACTION = "Transaction"
    INVOICE = "Invoice"
    VENDOR = "Vendor"
    CUSTOMER = "Customer"
    ADDRESS = "Address"
    DATE = "Date"
    AMOUNT = "Amount"
    CURRENCY = "Currency"
    PAYMENT_REF = "PaymentReference"
    CONTRACT = "Contract"
    EMAIL = "Email"
    PHONE = "Phone"
    DOCUMENT = "Document"


class RelationType(str, Enum):
    OWNS = "OWNS"
    WORKS_FOR = "WORKS_FOR"
    PAID = "PAID"
    RECEIVED = "RECEIVED"
    TRANSFERRED_TO = "TRANSFERRED_TO"
    ISSUED = "ISSUED"
    INVOICED = "INVOICED"
    APPROVED = "APPROVED"
    REFERENCED_BY = "REFERENCED_BY"
    CONNECTED_TO = "CONNECTED_TO"
    HAS_ACCOUNT = "HAS_ACCOUNT"
    SUPPORTS = "SUPPORTS"
    VIOLATES = "VIOLATES"


class NormalizedDocument(BaseModel):
    document_id: str = Field(..., description="Unique ID for the document")
    filename: str = Field(..., description="Original filename")
    document_type: DocumentType = Field(..., description="Normalized document type")
    source: str = Field(default="ingestion", description="Source path or channel")
    ingestion_timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    sha3_256_hash: str = Field(..., description="SHA3-256 hash of raw document content")
    processing_status: ProcessingStatus = Field(default=ProcessingStatus.PENDING)
    extracted_text: str = Field(default="", description="Extracted plain text")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata key-values")


class Entity(BaseModel):
    entity_id: str
    name: str
    entity_type: EntityType
    document_id: str
    evidence_text: str = ""
    confidence: float = 1.0
    attributes: Dict[str, Any] = Field(default_factory=dict)


class Relationship(BaseModel):
    relationship_id: str
    source_id: str
    target_id: str
    relation_type: RelationType
    document_id: str
    evidence_text: str = ""
    confidence: float = 1.0


class Transaction(BaseModel):
    transaction_id: str
    sender_id: str
    sender_name: str
    receiver_id: str
    receiver_name: str
    amount: float
    currency: str = "USD"
    timestamp: str
    payment_reference: str = ""
    document_id: str = ""
    evidence_text: str = ""


class TransactionCycle(BaseModel):
    cycle_id: str
    entities_involved: List[str]
    transactions_involved: List[str]
    total_amount: float
    timestamps: List[str]
    cycle_length: int
    source_documents: List[str]
    evidence: List[str]
    risk_level: str = "Anomalous Cycle - Requires Investigation"
    explanation: str = ""


class AnomalySeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AnomalyCategory(str, Enum):
    UNUSUALLY_HIGH_AMOUNT = "Unusually High Amount"
    UNUSUALLY_FREQUENT = "Unusually Frequent Transactions"
    RAPID_MONEY_MOVEMENT = "Rapid Money Movement / Pass-Through"
    CIRCULAR_TRANSACTION = "Circular Transaction Loop"
    STRUCTURING_SPLITTING = "Structuring / Splitting Pattern (Smurfing)"
    UNEXPECTED_COUNTERPARTY = "Unexpected / Unverified Counterparty"
    MISSING_DOCUMENTATION = "Missing Invoice / Contract Documentation"
    DUPLICATE_TRANSACTION = "Duplicate Transaction Pattern"
    TEMPORAL_ANOMALY = "Temporal Anomaly (Off-hours / Weekend)"
    SEGREGATION_OF_DUTIES = "Segregation of Duties Violation"
    UNUSUAL_ACCOUNT_RELATIONSHIP = "Unusual Account Relationship"
    SUSPICIOUS_CLUSTER = "Suspicious Entity Cluster"


class AnomalyFinding(BaseModel):
    anomaly_id: str
    transaction_id: Optional[str] = None
    entity_id: Optional[str] = None
    anomaly_type: AnomalyCategory
    anomaly_score: float = Field(..., ge=0.0, le=1.0)
    severity: AnomalySeverity
    explanation: str
    supporting_features: Dict[str, Any] = Field(default_factory=dict)
    evidence_documents: List[str] = Field(default_factory=list)


class PolicyFinding(BaseModel):
    finding_id: str
    policy_title: str
    policy_section: str
    violation_type: str
    description: str
    relevance_score: float = 1.0
    supporting_evidence: List[str] = Field(default_factory=list)
    citation: str = ""


class LedgerEntry(BaseModel):
    event_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    event_type: str
    actor: str = "ApexForge-Engine"
    input_reference: str
    finding: str
    evidence: List[str] = Field(default_factory=list)
    previous_hash: str
    current_hash: str


class ForensicNarrativeSection(BaseModel):
    executive_summary: str = ""
    observed_facts: List[str] = Field(default_factory=list)
    derived_relationships: List[str] = Field(default_factory=list)
    anomalies: List[str] = Field(default_factory=list)
    hypotheses: List[str] = Field(default_factory=list)
    policy_violations: List[str] = Field(default_factory=list)
    unresolved_questions: List[str] = Field(default_factory=list)
