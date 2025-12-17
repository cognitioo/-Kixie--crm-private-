# Kixie → Rise CRM Integration

Webhook bridge that automatically creates leads in Rise CRM when calls are received through Kixie.

## 🚀 Quick Start

### 1. Deploy to Railway

1. Push this code to a GitHub repository
2. Go to [Railway.app](https://railway.app)
3. Create new project → Deploy from GitHub repo
4. Add environment variables (see below)
5. Deploy!

### 2. Configure Environment Variables

In Railway dashboard, add these variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `RISE_API_TOKEN` | Super Admin API token from Rise CRM | `eyJ0eXAiOiJKV1Q...` |
| `RISE_BASE_URL` | Rise CRM base URL | `https://abvcorpsystem.com` |
| `DEFAULT_OWNER_EMAIL` | Fallback owner email | `admin@company.com` |
| `DEFAULT_LEAD_STATUS_ID` | Lead status ID | `1` |
| `DEFAULT_LEAD_SOURCE_ID` | Lead source ID | `1` |
| `DEFAULT_OWNER_ID` | Default owner ID | `1` |

### 3. Configure Kixie Webhook

1. Go to Kixie settings → Webhooks
2. Add new webhook:
   - **URL**: `https://your-railway-app.up.railway.app/webhook/kixie/call`
   - **Event**: End of Call
3. Save and test!

---

## 📋 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info and status |
| `/health` | GET | Health check |
| `/webhook/kixie/call` | POST | Main webhook endpoint for Kixie calls |
| `/webhook/kixie/raw` | POST | Debug endpoint to see raw payloads |
| `/api/test-connection` | GET | Test Rise CRM API connection |
| `/api/test-lead` | GET | Create a test lead |

---

## 🔧 How It Works

```
Kixie Call Ends
      ↓
Kixie sends webhook → POST /webhook/kixie/call
      ↓
Server extracts: phone, caller name, agent email
      ↓
Creates lead in Rise CRM via API
      ↓
Lead appears in Rise CRM dashboard!
```

### Data Mapping

| Kixie Field | Rise CRM Field |
|-------------|----------------|
| `calleridName` | Company Name (Lead Name) |
| `tonumber` | Phone |
| `email` | Owner (matched by email or default) |

---

## 🔑 Getting Rise CRM IDs

### Find Owner ID
1. Go to Rise CRM → Team
2. Click on a team member
3. Look at URL: `/team_members/view/1` → Owner ID = `1`

### Find Lead Status/Source IDs
1. Go to Rise CRM → Leads → Create New
2. Use browser inspect (F12) on dropdowns
3. Check `value` attributes

---

## 🛠️ Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file with your config
cp .env.example .env

# Run locally
uvicorn main:app --reload --port 8000

# Test webhook
curl -X POST http://localhost:8000/webhook/kixie/call \
  -H "Content-Type: application/json" \
  -d '{"data":{"callDetails":{"tonumber":"+551199999999","calleridName":"Test Lead"}}}'
```

---

## ⚠️ Important Notes

1. **Super Admin Token**: Use the super admin token from Rise CRM API Management
2. **Cloudflare**: If Rise CRM uses Cloudflare, add a WAF rule to allow POST requests to `/api/`
3. **Duplicate Prevention**: The system tracks call IDs to prevent duplicate leads

---

## 📁 Project Structure

```
kixie/
├── main.py              # FastAPI app setup
├── config.py            # Settings from .env
├── models.py            # Data models
├── Dockerfile           # Railway deployment
├── requirements.txt     # Python dependencies
├── routes/
│   └── webhook.py       # Webhook endpoints
└── services/
    ├── rise_crm.py      # Rise CRM API client
    ├── lead_service.py  # Lead creation logic
    └── user_mapper.py   # Email → Owner ID mapping
```

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Token not found" | Check API token is correct and from API Management |
| 500 error on POST | Check Cloudflare WAF rules allow POST to /api/ |
| Lead not created | Verify owner_id, lead_status_id, lead_source_id exist |
| Duplicate leads | Call ID tracking prevents duplicates automatically |

---

## 📞 Support

For issues with this integration, check:
1. Railway deployment logs
2. Rise CRM API Management for token status
3. Kixie webhook delivery status
4. Feel free to tell about devloper about anything if gone wrong  or contact at wa
