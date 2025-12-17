import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.webhook import router as webhook_router
from services.rise_crm import rise_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Kixie → Rise CRM Bridge",
    description="Webhook bridge to create leads in Rise CRM from Kixie call events",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(webhook_router)


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "Kixie → Rise CRM Bridge",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "webhook": "POST /webhook/kixie/call",
            "health": "GET /health",
            "test": "GET /api/test-connection"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/api/test-connection")
async def test_connection():
    """Test connection to Rise CRM API."""
    result = await rise_client.test_connection()
    return result


@app.get("/api/test-lead")
async def test_lead_creation():
    """Test creating a lead (for debugging)."""
    from config import get_settings
    settings = get_settings()
    
    result = await rise_client.create_lead(
        company_name="Test Lead from Kixie Bridge",
        owner_id=settings.default_owner_id,
        lead_status_id=settings.default_lead_status_id,
        lead_source_id=settings.default_lead_source_id,
        phone="+5511999999999"
    )
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
