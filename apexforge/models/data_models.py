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
    currency: str = "INR"
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
    risk_level: str = "Anomalous Cycle - Requires Forensic Verification"
    explanation: str = ""


class AnomalySeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


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
    expected_baseline: str = ""
    observed_value: str = ""
    deviation_delta: str = ""
    evidence_location: str = ""
    audit_recommendation: str = ""
    status: str = "OPEN"  # OPEN, CORRECTED_DISALLOWED, ITC_REVERSED, SUBSTANTIATED, RESOLVED_COMMERCIAL
    auditor_resolution_notes: str = ""
    resolved_by: str = ""
    resolved_timestamp: str = ""
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


# --- MODULE A: AUDIT TRAIL MODELS ---
class AuditReviewStatus(str, Enum):
    OPEN = "OPEN"
    UNDER_REVIEW = "UNDER_REVIEW"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    RESOLVED = "RESOLVED"


class AuditEvent(BaseModel):
    event_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    user_id: str = "CA_AUDITOR_01"
    user_role: str = "Chartered Accountant / Forensic Auditor"
    action: str
    entity_type: str
    entity_id: str
    previous_value: Optional[str] = None
    new_value: Optional[str] = None
    source: str = "System"
    ai_model: str = "Gemini-Pro-Forensic"
    confidence_score: float = 1.0
    previous_hash: str = ""
    current_hash: str = ""
    reason: str = ""


# --- MODULE B: AUTO LEDGER GENERATION MODELS ---
class LedgerCategory(str, Enum):
    REVENUE_SALES = "Revenue / Sales"
    PURCHASE_EXPENSE = "Direct Purchase / Cost of Sales"
    INDIRECT_EXPENSE = "Indirect Administrative Expense"
    CURRENT_ASSET = "Current Asset / Bank / Cash"
    NON_CURRENT_ASSET = "Fixed / Capital Asset"
    CURRENT_LIABILITY = "Current Liability / Creditors"
    CAPITAL_ACCOUNT = "Capital / Equity Account"
    TAX_DUTIES = "TDS / GST Tax Liability"
    SUSPENSE = "Unclassified / Suspense Account"


class AutoLedgerEntry(BaseModel):
    entry_id: str
    transaction_id: str
    date: str
    description: str
    debit_account: str
    credit_account: str
    amount: float
    currency: str = "INR"
    category: LedgerCategory
    vendor_customer: str = ""
    gst_rate: float = 0.0
    itc_eligible: bool = True
    tds_section: str = ""
    confidence_score: float = 0.95
    source_document: str = ""
    status: AuditReviewStatus = AuditReviewStatus.OPEN
    ca_notes: str = ""


# --- MODULE C: BANK RECONCILIATION MODELS ---
class ReconciliationMatchStatus(str, Enum):
    MATCHED = "MATCHED"
    UNMATCHED_BANK = "UNMATCHED_BANK_STATEMENT"
    UNMATCHED_LEDGER = "UNMATCHED_BOOKS_LEDGER"
    DUPLICATE_ENTRY = "DUPLICATE_ENTRY"
    AMOUNT_MISMATCH = "AMOUNT_MISMATCH"
    DATE_MISMATCH = "TIMING_DATE_MISMATCH"
    BANK_CHARGES = "UNRECORDED_BANK_CHARGE"
    SUSPICIOUS_ROUTING = "SUSPICIOUS_CIRCULAR_ROUTING"


class BankReconciliationLine(BaseModel):
    line_id: str
    bank_date: str
    ledger_date: str = ""
    bank_description: str
    ledger_description: str = ""
    bank_amount: float
    ledger_amount: float = 0.0
    variance: float = 0.0
    status: ReconciliationMatchStatus
    source_bank_doc: str = ""
    source_ledger_ref: str = ""
    recommendation: str = ""


# --- MODULE D: AIS & FORM 26AS RECONCILIATION MODELS ---
class AISRecord(BaseModel):
    record_id: str
    pan: str
    financial_year: str = "FY 2024-25"
    info_code: str  # e.g., SFT-005, SFT-014, TDS-194C
    info_description: str
    source_reporter: str  # e.g. HDFC Bank, Infosys Ltd
    reported_amount: float
    book_recorded_amount: float = 0.0
    variance_amount: float = 0.0
    disallowance_section: str = ""  # e.g. Sec 40A(3), Sec 68, Sec 194C
    compliance_risk: str = "NORMAL"  # HIGH_RISK, MEDIUM_RISK, NORMAL
    status: AuditReviewStatus = AuditReviewStatus.OPEN
    evidence_ref: str = ""


# --- MODULE F: UNIFIED MULTI-WAY RECONCILIATION MATRIX ---
class UnifiedReconciliationMatrix(BaseModel):
    matrix_id: str
    transaction_id: str
    counterparty: str
    amount: float
    bank_reconciled: bool
    ledger_posted: bool
    ais_matched: bool
    invoice_backed: bool
    graph_cycle_detected: bool
    forensic_risk_score: float
    unified_status: str
    audit_action: str


# --- MODULE I: AUDIT WORKING PAPERS ---
class WorkingPaperSchedule(BaseModel):
    schedule_id: str
    schedule_name: str
    statutory_clause: str  # Form 3CD Clause 21(b), Clause 31(a), etc.
    system_findings_summary: str
    ca_auditor_observations: str
    ca_auditor_conclusion: str
    audit_status: AuditReviewStatus = AuditReviewStatus.OPEN


class AuditWorkingPaper(BaseModel):
    paper_id: str
    financial_year: str = "FY 2024-25"
    entity_name: str = "Apex Global Corp India Pvt Ltd"
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    sa240_fraud_findings: List[str] = Field(default_factory=list)
    sa250_statutory_compliance: List[str] = Field(default_factory=list)
    schedules: List[WorkingPaperSchedule] = Field(default_factory=list)
    tamper_hash_chain_status: str = "SHA3-256 VERIFIED"
    auditor_signoff_notes: str = ""

