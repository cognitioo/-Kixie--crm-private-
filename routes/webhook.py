import logging
from fastapi import APIRouter, HTTPException, Request
from models import KixieCallEvent
from services.lead_service import create_lead_from_call

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook", tags=["webhook"])


def parse_kixie_payload(raw_data: dict) -> KixieCallEvent:
    """
    Parse the nested Kixie webhook payload into our KixieCallEvent model.
    
    Kixie sends: { "data": { "callDetails": {...}, "number": "..." } }
    We need to extract and map the fields based on call direction.
    """
    data = raw_data.get("data", raw_data)  # Handle both nested and flat
    call_details = data.get("callDetails", data)
    
    # Determine call direction
    call_type = call_details.get("calltype", "").lower()
    is_outgoing = call_type == "outgoing"
    
    # Extract phone number (the contact's number)
    # For outgoing: tonumber is the contact being called
    # For incoming: fromnumber is the contact calling
    if is_outgoing:
        phone = (
            call_details.get("tonumber") or 
            call_details.get("tonumber164") or
            data.get("number") or
            ""
        )
    else:
        phone = (
            call_details.get("fromnumber") or 
            call_details.get("fromnumber164") or
            data.get("customernumber") or
            data.get("number") or
            ""
        )
    
    # Extract contact name based on call direction
    # For outgoing calls: destinationName is the called party (contact)
    # For incoming calls: calleridName is the caller (contact)
    # NOTE: Rise CRM only accepts alphabet characters in company_name
    if is_outgoing:
        # For outgoing calls, use destinationName
        dest_name = call_details.get("destinationName")
        if dest_name and dest_name.strip():
            # Clean the name - keep only letters and spaces
            clean_name = ''.join(c for c in dest_name if c.isalpha() or c.isspace()).strip()
            contact_name = clean_name if clean_name else "Kixie Outbound Contact"
        else:
            # Use generic name when no contact name available
            contact_name = "Kixie Outbound Contact"
    else:
        # For incoming calls, use calleridName
        caller_name = (
            call_details.get("calleridName") or
            f"{call_details.get('fname', '')} {call_details.get('lname', '')}".strip()
        )
        if caller_name and caller_name.strip():
            # Clean the name - keep only letters and spaces
            clean_name = ''.join(c for c in caller_name if c.isalpha() or c.isspace()).strip()
            contact_name = clean_name if clean_name else "Kixie Inbound Contact"
        else:
            # Use generic name when no contact name available
            contact_name = "Kixie Inbound Contact"
    
    # Extract agent email (the Kixie user who made/received the call)
    agent_email = call_details.get("email")
    
    # Extract call ID
    call_id = call_details.get("callid") or call_details.get("externalid")
    
    logger.info(f"Call type: {call_type}, Contact name: {contact_name}, Phone: {phone}")
    
    return KixieCallEvent(
        phone_number=phone,
        contact_name=contact_name,
        agent_email=agent_email,
        call_id=call_id,
        call_duration=call_details.get("duration"),
        call_status=call_details.get("callstatus"),
        recording_url=call_details.get("recordingurl"),
        contact_address=None
    )


@router.post("/kixie/call")
async def handle_kixie_call(request: Request):
    """
    Handle incoming call events from Kixie.
    Creates a lead in Rise CRM for each call.
    """
    try:
        raw_payload = await request.json()
        logger.info(f"Received Kixie webhook: {raw_payload.get('data', {}).get('hookevent', 'unknown')}")
        
        # Parse the nested Kixie payload
        event = parse_kixie_payload(raw_payload)
        logger.info(f"Parsed call event: {event.phone_number} from {event.agent_email}")
        
        result = await create_lead_from_call(event)
        return {"success": True, "data": result}
    
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error processing call event: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create lead: {str(e)}")


@router.post("/kixie/raw")
async def handle_kixie_raw(request: Request):
    """
    Debug endpoint to see raw Kixie payload.
    """
    body = await request.json()
    logger.info(f"Raw Kixie payload: {body}")
    return {"received": body}
