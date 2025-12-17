from pydantic import BaseModel, Field
from typing import Optional


class KixieCallEvent(BaseModel):
    """Incoming webhook payload from Kixie call events."""
    
    # Contact information
    contact_name: Optional[str] = Field(default=None, description="Contact name from Kixie")
    phone_number: str = Field(..., description="Phone number (required)")
    contact_address: Optional[str] = Field(default=None, description="Contact address")
    
    # Call metadata
    call_id: Optional[str] = Field(default=None, description="Unique call identifier")
    agent_email: Optional[str] = Field(default=None, description="Kixie agent email")
    agent_name: Optional[str] = Field(default=None, description="Kixie agent name")
    
    # Optional fields that may come from Kixie
    call_duration: Optional[int] = Field(default=None, description="Call duration in seconds")
    call_status: Optional[str] = Field(default=None, description="Call status/disposition")
    recording_url: Optional[str] = Field(default=None, description="Call recording URL")


class RiseLeadCreate(BaseModel):
    """Payload for creating a lead in Rise CRM."""
    
    company_name: str = Field(..., description="Lead/Contact name")
    phone: str = Field(..., description="Phone number")
    address: Optional[str] = Field(default="", description="Address")
    owner_id: int = Field(..., description="Rise CRM user ID")
    lead_status_id: int = Field(..., description="Lead status ID")
    lead_source_id: int = Field(..., description="Lead source ID")


class RiseUser(BaseModel):
    """Rise CRM user representation."""
    
    id: int
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    
    class Config:
        extra = "ignore"  # Ignore extra fields from API


class RiseLeadStatus(BaseModel):
    """Rise CRM lead status representation."""
    
    id: int
    title: str
    
    class Config:
        extra = "ignore"


class RiseLeadSource(BaseModel):
    """Rise CRM lead source representation."""
    
    id: int
    title: str
    
    class Config:
        extra = "ignore"
