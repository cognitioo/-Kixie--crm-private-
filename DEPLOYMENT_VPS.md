# VPS Deployment Guide (CyberPanel + Hostinger)

This guide explains how to deploy the Kixie → Rise CRM webhook on a VPS with CyberPanel.

## Prerequisites

- VPS with CyberPanel installed
- SSH access to your server
- A subdomain (e.g., `kixie-webhook.yourdomain.com`)

---

## Step 1: Create Website in CyberPanel

1. Log in to CyberPanel
2. Go to **Websites** → **Create Website**
3. Enter:
   - **Domain Name**: `kixie-webhook.yourdomain.com`
   - **Email**: Your email
   - **PHP**: Any (we won't use PHP)
4. Click **Create Website**
5. Go to **SSL** → **Issue SSL** for your subdomain (Important for HTTPS!)

---

## Step 2: Connect via SSH

Open terminal/PowerShell and connect:

```bash
ssh root@your-server-ip
```

---

## Step 3: Install Python Dependencies

```bash
# Update package list
apt update

# Install Python 3 and pip
apt install python3 python3-pip python3-venv -y

# Install supervisor (to keep the app running)
apt install supervisor -y
```

---

## Step 4: Upload Project Files

Navigate to your website directory:

```bash
cd /home/kixie-webhook.yourdomain.com
mkdir webhook
cd webhook
```

Upload these files to this directory:
- `main.py`
- `config.py`
- `models.py`
- `requirements.txt`
- `routes/` folder
- `services/` folder
- `.env` file (with your configuration)

You can use:
- **CyberPanel File Manager**: Upload to `/home/kixie-webhook.yourdomain.com/webhook/`
- **SFTP**: Connect with FileZilla or similar
- **SCP**: `scp -r /local/path/* root@server:/home/kixie-webhook.yourdomain.com/webhook/`

---

## Step 5: Create Virtual Environment

```bash
cd /home/kixie-webhook.yourdomain.com/webhook

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Step 6: Create .env File

```bash
nano .env
```

Add your configuration:

```
RISE_API_TOKEN=your_token_here
RISE_BASE_URL=https://abvcorpsystem.com
DEFAULT_OWNER_EMAIL=eder09062016@gmail.com
DEFAULT_LEAD_STATUS_ID=1
MISSED_CALL_STATUS_ID=1
DEFAULT_LEAD_SOURCE_ID=1
DEFAULT_OWNER_ID=1
```

Save with `Ctrl+X`, then `Y`, then `Enter`.

---

## Step 7: Test the Application

```bash
cd /home/kixie-webhook.yourdomain.com/webhook
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Press `Ctrl+C` to stop.

---

## Step 8: Configure Supervisor (Auto-start)

Create a supervisor config file:

```bash
nano /etc/supervisor/conf.d/kixie-webhook.conf
```

Add this content:

```ini
[program:kixie-webhook]
command=/home/kixie-webhook.yourdomain.com/webhook/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
directory=/home/kixie-webhook.yourdomain.com/webhook
user=root
autostart=true
autorestart=true
stderr_logfile=/var/log/kixie-webhook.err.log
stdout_logfile=/var/log/kixie-webhook.out.log
```

Save and exit.

Reload supervisor:

```bash
supervisorctl reread
supervisorctl update
supervisorctl start kixie-webhook
```

Check status:

```bash
supervisorctl status kixie-webhook
```

---

## Step 9: Configure OpenLiteSpeed Proxy

In CyberPanel:

1. Go to **Websites** → **List Websites**
2. Click on your subdomain → **vHost Conf**
3. Add this to the configuration:

```
extprocessor kixie {
  type                    proxy
  address                 127.0.0.1:8000
  maxConns                100
  initTimeout             60
  retryTimeout            0
  respBuffer              0
}

context / {
  type                    proxy
  handler                 kixie
  addDefaultCharset       off
}
```

4. Click **Save**
5. Restart OpenLiteSpeed: **Server Status** → **Restart LiteSpeed**

---

## Step 10: Verify Deployment

Visit your subdomain:

```
https://kixie-webhook.yourdomain.com/
```

You should see:
```json
{
  "name": "Kixie → Rise CRM Bridge",
  "version": "1.0.0",
  "status": "running"
}
```

---

## Step 11: Update Kixie Webhook URL

In Kixie → Custom CRM settings, update the webhook URL to:

```
https://kixie-webhook.yourdomain.com/webhook/kixie/call
```

---

## Troubleshooting

### Check Logs

```bash
# Application logs
tail -f /var/log/kixie-webhook.out.log
tail -f /var/log/kixie-webhook.err.log

# Supervisor status
supervisorctl status

# Restart application
supervisorctl restart kixie-webhook
```

### Common Issues

| Issue | Solution |
|-------|----------|
| 502 Bad Gateway | Check if supervisor is running: `supervisorctl status` |
| SSL Error | Issue SSL certificate in CyberPanel |
| Port Already in Use | Kill existing process: `fuser -k 8000/tcp` |
| Permission Denied | Run as root or fix permissions |

---

## File Structure on Server

```
/home/kixie-webhook.yourdomain.com/
└── webhook/
    ├── main.py
    ├── config.py
    ├── models.py
    ├── requirements.txt
    ├── .env
    ├── venv/
    ├── routes/
    │   ├── __init__.py
    │   └── webhook.py
    └── services/
        ├── __init__.py
        ├── rise_crm.py
        ├── lead_service.py
        └── user_mapper.py
```

---

## Support

If you encounter issues:
1. Check the logs: `tail -f /var/log/kixie-webhook.err.log`
2. Verify supervisor status: `supervisorctl status`
3. Test API connection: `curl https://kixie-webhook.yourdomain.com/health`
