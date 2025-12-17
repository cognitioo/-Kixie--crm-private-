import logging
from config import get_settings
from models import KixieCallEvent
from services.rise_crm import rise_client
from services.user_mapper import user_mapper

logger = logging.getLogger(__name__)

# Track processed call IDs to prevent duplicates
_processed_calls: set[str] = set()


def get_lead_status_id(call_status: str | None, settings) -> int:
    """
    Map Kixie call status to Rise CRM lead status ID.
    
    Args:
        call_status: Kixie call status (answered, not answered, etc.)
        settings: Application settings
        
    Returns:
        Lead status ID for Rise CRM
    """
    if not call_status:
        return settings.default_lead_status_id
    
    call_status_lower = call_status.lower().strip()
    
    # Map Kixie call statuses to Rise CRM lead statuses
    if call_status_lower in ("answered", "completed"):
        return settings.default_lead_status_id
    elif call_status_lower in ("not answered", "missed", "no answer", "busy", "failed"):
        return settings.missed_call_status_id
    else:
        # Default for unknown statuses
        return settings.default_lead_status_id


async def create_lead_from_call(event: KixieCallEvent) -> dict:
    """
    Create a lead in Rise CRM from a Kixie call event.
    
    Returns the result dict containing status and details.
    """
    # Check for duplicate call
    if event.call_id and event.call_id in _processed_calls:
        logger.info(f"Duplicate call ignored: {event.call_id}")
        return {"status": "duplicate", "call_id": event.call_id}
    
    settings = get_settings()
    
    # Resolve contact name (use "Unknown Name" if not provided)
    contact_name = event.contact_name.strip() if event.contact_name else "Unknown Name"
    if not contact_name:
        contact_name = "Unknown Name"
    
    # Resolve owner ID from Kixie agent email
    owner_id = await user_mapper.get_owner_id(event.agent_email)
    
    # Get lead status based on call status (answered/not answered)
    lead_status_id = get_lead_status_id(event.call_status, settings)
    
    logger.info(f"Call status '{event.call_status}' -> Lead status ID: {lead_status_id}")
    
    # Create lead in Rise CRM
    result = await rise_client.create_lead(
        company_name=contact_name,
        owner_id=owner_id,
        lead_status_id=lead_status_id,
        lead_source_id=settings.default_lead_source_id,
        phone=event.phone_number,
        address=event.contact_address or ""
    )
    
    # Check if creation was successful
    if result.get("status") is True:
        # Mark call as processed
        if event.call_id:
            _processed_calls.add(event.call_id)
            # Limit set size to prevent memory issues
            if len(_processed_calls) > 10000:
                _processed_calls.clear()
        
        logger.info(f"Lead created: {contact_name} ({event.phone_number}) -> Owner ID: {owner_id}")
        
        return {
            "status": "created",
            "lead_name": contact_name,
            "phone": event.phone_number,
            "owner_id": owner_id,
            "rise_response": result
        }
    else:
        logger.error(f"Lead creation failed: {result.get('message')}")
        return {
            "status": "failed",
            "lead_name": contact_name,
            "phone": event.phone_number,
            "error": result.get("message", "Unknown error"),
            "rise_response": result
        }
