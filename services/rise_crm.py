import httpx
import logging
from typing import Optional, Any
from config import get_settings

logger = logging.getLogger(__name__)


class RiseCRMClient:
    """
    Client for Rise CRM REST API.
    
    Based on the official API documentation:
    - Uses `authtoken` header for authentication
    - Uses multipart-form data for POST/PUT operations
    - Endpoints are at /index.php/api/...
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.rise_base_url.rstrip("/")
        self.token = self.settings.rise_api_token
    
    def _get_headers(self) -> dict:
        """Get headers for API requests."""
        return {
            "authtoken": self.token
        }
    
    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        data: dict = None,
        use_form: bool = True
    ) -> dict:
        """
        Make HTTP request to Rise CRM API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Data to send (for POST/PUT)
            use_form: If True, send as form data; if False, send as JSON
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        async with httpx.AsyncClient() as client:
            try:
                if method.upper() in ("POST", "PUT") and data:
                    if use_form:
                        # Rise API uses multipart-form for data operations
                        response = await client.request(
                            method=method,
                            url=url,
                            headers=headers,
                            data=data,  # Form data
                            timeout=30.0
                        )
                    else:
                        response = await client.request(
                            method=method,
                            url=url,
                            headers={**headers, "Content-Type": "application/json"},
                            json=data,
                            timeout=30.0
                        )
                else:
                    response = await client.request(
                        method=method,
                        url=url,
                        headers=headers,
                        timeout=30.0
                    )
                
                logger.info(f"{method} {url} -> {response.status_code}")
                
                # Try to parse JSON response
                try:
                    result = response.json()
                    # Log full response if error
                    if response.status_code >= 400:
                        logger.error(f"API Error Response: {result}")
                    else:
                        logger.debug(f"Response: {result}")
                    return result
                except Exception:
                    logger.error(f"Raw response: {response.text}")
                    return {"status": False, "message": response.text}
                    
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
                raise
            except httpx.RequestError as e:
                logger.error(f"Request error: {str(e)}")
                raise
    
    async def get_staff_owners(self) -> list[dict]:
        """
        Fetch all staff owners from Rise CRM.
        Endpoint: GET /index.php/api/staff_owner
        """
        result = await self._request("GET", "/index.php/api/staff_owner")
        
        # Handle different response formats
        if isinstance(result, list):
            return result
        elif isinstance(result, dict):
            if "status" in result and result["status"] is False:
                logger.warning(f"Staff fetch failed: {result.get('message')}")
                return []
            # Could be a single item or have data key
            if "data" in result:
                return result["data"] if isinstance(result["data"], list) else [result["data"]]
            return [result]
        return []
    
    async def create_lead(
        self,
        company_name: str,
        owner_id: int,
        lead_status_id: int,
        lead_source_id: int,
        phone: str = "",
        address: str = "",
        city: str = "",
        state: str = "",
        zip_code: str = "",
        country: str = "",
        website: str = "",
        vat_number: str = ""
    ) -> dict:
        """
        Create a new lead in Rise CRM.
        
        Endpoint: POST /index.php/api/leads
        
        Required fields:
        - company_name: Lead name
        - owner_id: Lead owner ID
        - lead_status_id: Lead status ID
        - lead_source_id: Lead source ID
        """
        payload = {
            "company_name": company_name,
            "owner_id": str(owner_id),
            "lead_status_id": str(lead_status_id),
            "lead_source_id": str(lead_source_id),
        }
        
        # Add optional fields if provided
        if phone:
            payload["phone"] = phone
        if address:
            payload["address"] = address
        if city:
            payload["city"] = city
        if state:
            payload["state"] = state
        if zip_code:
            payload["zip"] = zip_code
        if country:
            payload["country"] = country
        if website:
            payload["website"] = website
        if vat_number:
            payload["vat_number"] = vat_number
        
        logger.info(f"Creating lead: {company_name} (phone: {phone})")
        result = await self._request("POST", "/index.php/api/leads", data=payload)
        
        if result.get("status") is True:
            logger.info(f"Lead created successfully: {result.get('message')}")
        else:
            logger.error(f"Lead creation failed: {result.get('message')}")
        
        return result
    
    async def get_leads(self, lead_id: Optional[int] = None) -> Any:
        """
        Get leads from Rise CRM.
        
        Endpoint: GET /index.php/api/leads/:leadid
        """
        if lead_id:
            endpoint = f"/index.php/api/leads/{lead_id}"
        else:
            endpoint = "/index.php/api/leads"
        
        return await self._request("GET", endpoint)
    
    async def test_connection(self) -> dict:
        """Test the API connection by fetching staff owners."""
        try:
            staff = await self.get_staff_owners()
            return {
                "status": "connected",
                "staff_count": len(staff),
                "staff": staff
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }


# Singleton instance
rise_client = RiseCRMClient()
