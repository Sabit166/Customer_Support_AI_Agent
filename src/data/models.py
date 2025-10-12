"""Data models for the Customer Support AI Agent.

This module provides Pydantic models and a lightweight dataclass for user
context. Models include sensible defaults and enums to make them easier to
use during testing and in the UI (e.g., `UserContext()` may be created with
no arguments).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional
import uuid

from pydantic import BaseModel, Field


class ResponseType(str, Enum):
    INFORMATION = "information"
    COMPLAINT = "complaint_resolution"
    TECHNICAL = "technical_support"


class Priority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class Category(str, Enum):
    TECHNICAL = "Technical"
    BILLING = "Billing"
    SERVICE = "Service"
    GENERAL = "General"


class Status(str, Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    CLOSED = "Closed"


class ServiceResponse(BaseModel):
    """Standardized response returned by agents.

    Fields are intentionally simple so the UI can render them consistently.
    """
    response_type: ResponseType = Field(ResponseType.INFORMATION, description="Type of response")
    content: str = Field(..., description="Main response content for the customer")
    actions_taken: List[str] = Field(default_factory=list, description="List of actions taken (e.g., 'Created ticket')")
    ticket_id: Optional[str] = Field(None, description="Complaint ticket ID if created")
    next_steps: Optional[str] = Field(None, description="What happens next or what customer should do")
    escalation_needed: bool = Field(False, description="Whether this issue needs human escalation")


class TechnicalResponse(BaseModel):
    """Specialized response for technical support interactions.
    
    Includes technical-specific fields for troubleshooting and diagnostics.
    """
    issue_type: str = Field(..., description="Type of technical issue (connectivity, speed, equipment, etc.)")
    diagnosis: str = Field(..., description="Technical diagnosis or assessment of the problem")
    solution_steps: List[str] = Field(default_factory=list, description="Step-by-step troubleshooting instructions")
    equipment_involved: List[str] = Field(default_factory=list, description="Equipment mentioned (router, modem, cables, etc.)")
    estimated_resolution_time: Optional[str] = Field(None, description="Expected time to resolve the issue")
    requires_technician: bool = Field(False, description="Whether on-site technician visit is needed")
    follow_up_needed: bool = Field(False, description="Whether follow-up contact is required")
    customer_instructions: str = Field(..., description="Clear instructions for the customer")
    escalation_level: str = Field("Level 1", description="Support escalation level (Level 1, Level 2, Level 3)")


class ComplaintTicket(BaseModel):
    ticket_id: str = Field(..., description="Unique ticket identifier")
    customer_name: str = Field(..., description="Name of the customer")
    complaint_description: str = Field(..., description="Detailed description of the complaint")
    priority: Priority = Field(Priority.MEDIUM, description="Priority level")
    assigned_agent: Optional[str] = Field(None, description="Agent assigned to handle this ticket")
    category: Category = Field(Category.GENERAL, description="Complaint category")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: Status = Field(Status.OPEN, description="Ticket status")

    model_config = {"use_enum_values": True}


@dataclass
class UserContext:
    """Lightweight context object for a user session.

    Designed to be easy to construct in tests and UI examples (no required
    positional args). `user_id` will be created automatically if omitted.
    """
    user_id: str = field(default_factory=lambda: f"CUST-{uuid.uuid4().hex[:8]}")
    user_name: Optional[str] = "Customer"
    current_plan: Optional[str] = None  # "Basic", "Standard", "Premium"
    service_area: Optional[str] = None
    account_status: Optional[str] = "Active"
    preferred_contact: Optional[str] = "Email"
    session_start: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "user_name": self.user_name,
            "current_plan": self.current_plan,
            "service_area": self.service_area,
            "account_status": self.account_status,
            "preferred_contact": self.preferred_contact,
            "session_start": self.session_start.isoformat(),
        }
