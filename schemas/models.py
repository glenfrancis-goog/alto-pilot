"""Pydantic Schema Definitions for HR Policy Agent."""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field

class PolicyCitation(BaseModel):
    policy_name: str = Field(description="Name of the official HR policy evaluated (e.g. Parental Leave Policy)")
    section: str = Field(description="Section heading or clause referenced (e.g. Section 1: Eligibility & Scope)")
    rule_summary: str = Field(description="Verbatim rule requirement applied")

class HREligibilityDecision(BaseModel):
    employee_id: str = Field(description="The unique employee identifier evaluated (e.g. EMP-101)")
    employee_name: Optional[str] = Field(default=None, description="Employee full name if resolved")
    policy_category: Literal["PARENTAL_LEAVE", "ANNUAL_LEAVE", "REMOTE_WORK", "UNCOVERED"] = Field(
        description="The categorized HR domain"
    )
    status: Literal["ELIGIBLE", "INELIGIBLE", "ESCALATE_TO_HRBP"] = Field(
        description="Deterministic decision status"
    )
    requested_days: int = Field(description="Total days requested by the user")
    approved_days: int = Field(description="Total days verified and approved by policy (0 if ineligible or escalated)")
    citations: List[PolicyCitation] = Field(description="Grounded citations from OKF policy documents")
    reasoning: str = Field(description="Detailed explanation of the determination, citing verified tenure, dates, and rules")
    action_required: str = Field(description="Explicit operational next step for the employee, manager, or HRBP")
