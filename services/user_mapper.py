import logging
from typing import Optional
from config import get_settings
from services.rise_crm import rise_client

logger = logging.getLogger(__name__)


class UserMapper:
    """
    Maps Kixie user emails to Rise CRM user IDs.
    
    Since Rise CRM doesn't have a direct users/email lookup API,
    we fetch staff_owner and try to match by email.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self._staff_cache: Optional[list[dict]] = None
        self._default_owner_id: Optional[int] = None
    
    async def _get_staff(self, force_refresh: bool = False) -> list[dict]:
        """Get cached staff list."""
        if self._staff_cache is None or force_refresh:
            self._staff_cache = await rise_client.get_staff_owners()
        return self._staff_cache
    
    async def find_user_by_email(self, email: str) -> Optional[dict]:
        """
        Find a Rise CRM user/staff by email.
        Returns the user dict if found, None otherwise.
        """
        staff = await self._get_staff()
        email_lower = email.lower()
        
        for person in staff:
            # Try common email field names
            person_email = person.get("email", "")
            if person_email and person_email.lower() == email_lower:
                return person
        
        return None
    
    async def get_owner_id(self, kixie_email: Optional[str] = None) -> int:
        """
        Get the Rise CRM owner ID for a given Kixie agent email.
        Falls back to default owner if no match found.
        
        Returns:
            int: The Rise CRM user/owner ID
        """
        # Try to match by email
        if kixie_email:
            user = await self.find_user_by_email(kixie_email)
            if user and "id" in user:
                owner_id = int(user["id"])
                logger.info(f"Mapped {kixie_email} to Rise owner ID {owner_id}")
                return owner_id
            else:
                logger.warning(f"No Rise user found for email: {kixie_email}")
        
        # Use default owner
        default_id = self.settings.default_owner_id
        logger.info(f"Using default owner ID: {default_id}")
        return default_id


# Singleton instance
user_mapper = UserMapper()
