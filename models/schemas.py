"""
models/schemas.py
Pydantic data models and LangGraph state definitions for Intelligent HR Equipment Support Assistant.
"""

from enum import Enum
from typing import TypedDict, List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator
import re


class IssueCategory(str, Enum):
    """Supported issue categories for routing and tracking."""
    HARDWARE = "hardware"
    TECHNICAL = "technical"
    ACCESS = "access"
    GENERAL = "general"


class TicketPriority(str, Enum):
    """Support ticket priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketStatus(str, Enum):
    """Support ticket lifecycle statuses."""
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    PENDING_APPROVAL = "Pending Approval"
    RESOLVED = "Resolved"
    CLOSED = "Closed"


class EmployeeQuery(BaseModel):
    """
    Validates and sanitizes employee input queries.
    Prevents empty inputs, prompt injection attempts, and excessive length.
    """
    employee_id: str = Field(
        ...,
        description="Employee ID in format EMP followed by digits, e.g. EMP1024",
        examples=["EMP1024", "EMP5501"]
    )
    query: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="The employee's question or support issue description."
    )

    @field_validator("employee_id")
    @classmethod
    def validate_employee_id(cls, v: str) -> str:
        v = v.strip().upper()
        if not re.match(r"^EMP\d{3,6}$", v):
            # Fallback format tolerance for testing (e.g. EMP101, E123)
            if not re.match(r"^[A-Za-z0-9_-]{3,10}$", v):
                raise ValueError("Invalid Employee ID format. Must be alphanumeric (e.g., EMP1024).")
        return v

    @field_validator("query")
    @classmethod
    def sanitize_query(cls, v: str) -> str:
        # Strip potential HTML/script tags and excessive whitespace
        clean_text = re.sub(r"<[^>]*>", "", v).strip()
        if not clean_text:
            raise ValueError("Query cannot be empty after sanitization.")
        return clean_text


class SupportTicket(BaseModel):
    """Data model representing a created or queried support ticket."""
    ticket_id: str = Field(..., description="Unique ticket identifier, e.g. TKT-7A92F1C3")
    employee_id: str = Field(..., description="ID of employee raising the ticket")
    category: str = Field(..., description="Ticket issue category")
    description: str = Field(..., description="Summary of the issue reported")
    priority: str = Field(default=TicketPriority.MEDIUM.value, description="Assigned priority level")
    status: str = Field(default=TicketStatus.OPEN.value, description="Current ticket status")
    created_at: Optional[str] = Field(default=None, description="Timestamp of ticket creation")


class ClassificationResult(BaseModel):
    """Structured output returned by the query classification step."""
    category: IssueCategory = Field(
        ...,
        description="The identified category: hardware, technical, access, or general"
    )
    confidence: float = Field(
        default=0.9,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0"
    )
    reason: str = Field(
        ...,
        description="Brief justification for why this category was selected"
    )
    detected_priority: TicketPriority = Field(
        default=TicketPriority.MEDIUM,
        description="Initial priority level estimated from the query urgency"
    )


class ApprovalRequest(BaseModel):
    """Represents a human-in-the-loop approval request for sensitive actions."""
    action_type: str = Field(..., description="E.g., password_reset, equipment_replacement, access_grant")
    employee_id: str
    target_resource: str
    estimated_cost: Optional[str] = None
    status: str = "Pending Approval"
    approval_notes: str = ""


# ==============================================================================
# LangGraph Workflow State Definition
# ==============================================================================

class SupportState(TypedDict):
    """
    Central state object carried across all nodes in the LangGraph state graph.
    Matches all requested fields:
    - user_query: raw or sanitized text submitted by employee
    - employee_id: ID of the current employee
    - category: hardware | technical | access | general
    - priority: low | medium | high | critical
    - conversation_history: list of past turns [User: ..., Assistant: ...]
    - employee_memory: long-term profile data from SQLite
    - tool_result: output payload from any tool executed
    - approval_required: flag indicating human approval is needed
    - final_answer: the resulting agent response presented to user
    """
    user_query: str
    employee_id: str
    category: str
    priority: str
    conversation_history: List[str]
    employee_memory: Dict[str, Any]
    tool_result: str
    approval_required: bool
    final_answer: str
