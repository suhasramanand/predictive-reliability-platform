"""
Webhook Service
Sends real-time notifications for anomalies and incidents
"""
import os
import logging
import hmac
import hashlib
import asyncio
from datetime import datetime
from typing import List, Dict, Optional
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel, HttpUrl
import requests
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Webhook Service", version="1.0.0")

# Configuration
ANOMALY_SERVICE_URL = os.getenv("ANOMALY_SERVICE_URL", "http://anomaly-service:8080")
CHECK_INTERVAL = int(os.getenv("WEBHOOK_CHECK_INTERVAL", "30"))

# Webhook storage (should be database in production)
webhooks_db: Dict[str, dict] = {}
webhook_history = []

class Webhook(BaseModel):
    url: HttpUrl
    events: List[str] = ["anomaly.detected", "incident.started", "incident.resolved"]
    secret: Optional[str] = None
    enabled: bool = True
    headers: Dict[str, str] = {}

class WebhookEvent(BaseModel):
    event: str
    timestamp: str
    data: dict

def generate_signature(payload: str, secret: str) -> str:
    """Generate HMAC signature for webhook payload"""
    return hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()

async def send_webhook(webhook_id: str, event: WebhookEvent):
    """Send webhook notification"""
    webhook = webhooks_db.get(webhook_id)
    if not webhook or not webhook.get('enabled'):
        return
    
    # Check if this event is subscribed
    if event.event not in webhook.get('events', []):
        return
    
    try:
        payload = event.dict()
        payload_str = json.dumps(payload)
        
        headers = webhook.get('headers', {}).copy()
        headers['Content-Type'] = 'application/json'
        headers['X-Webhook-Event'] = event.event
        headers['X-Webhook-ID'] = webhook_id
        
        # Add signature if secret provided
        if webhook.get('secret'):
            signature = generate_signature(payload_str, webhook['secret'])
            headers['X-Webhook-Signature'] = f"sha256={signature}"
        
        # Send webhook
        response = requests.post(
            webhook['url'],
            data=payload_str,
            headers=headers,
            timeout=10
        )
        
        # Log result
        webhook_log = {
            "webhook_id": webhook_id,
            "event": event.event,
            "status_code": response.status_code,
            "success": 200 <= response.status_code < 300,
            "timestamp": datetime.utcnow().isoformat()
        }
        webhook_history.append(webhook_log)
        
        logger.info(f"Webhook sent: {webhook_id} - {event.event} - {response.status_code}")
        
    except Exception as e:
        logger.error(f"Error sending webhook {webhook_id}: {e}")
        webhook_history.append({
            "webhook_id": webhook_id,
            "event": event.event,
            "error": str(e),
            "success": False,
            "timestamp": datetime.utcnow().isoformat()
        })

async def monitor_anomalies():
    """Background task to monitor anomalies and send webhooks"""
    logger.info("Starting webhook monitoring")
    last_anomalies = set()
    
    while True:
        try:
            # Get current anomalies
            response = requests.get(f"{ANOMALY_SERVICE_URL}/anomalies", timeout=5)
            if response.status_code == 200:
                data = response.json()
                current_anomalies = data.get('anomalies', [])
                
                # Detect new anomalies
                for anomaly in current_anomalies:
                    anomaly_id = f"{anomaly['service']}_{anomaly['metric']}_{anomaly['timestamp']}"
                    
                    if anomaly_id not in last_anomalies:
                        # New anomaly detected
                        event = WebhookEvent(
                            event="anomaly.detected",
                            timestamp=datetime.utcnow().isoformat(),
                            data=anomaly
                        )
                        
                        # Send to all webhooks
                        for webhook_id in list(webhooks_db.keys()):
                            await send_webhook(webhook_id, event)
                        
                        last_anomalies.add(anomaly_id)
                
                # Clean old anomalies
                if len(last_anomalies) > 1000:
                    last_anomalies.clear()
                    
        except Exception as e:
            logger.error(f"Error in webhook monitoring: {e}")
        
        await asyncio.sleep(CHECK_INTERVAL)

@app.on_event("startup")
async def startup():
    """Start background monitoring"""
    asyncio.create_task(monitor_anomalies())

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy", "service": "webhook-service"}

@app.post("/webhooks")
async def create_webhook(webhook: Webhook):
    """Register a new webhook"""
    import uuid
    webhook_id = f"webhook_{uuid.uuid4().hex[:8]}"
    
    webhooks_db[webhook_id] = {
        "id": webhook_id,
        "url": str(webhook.url),
        "events": webhook.events,
        "secret": webhook.secret,
        "enabled": webhook.enabled,
        "headers": webhook.headers,
        "created_at": datetime.utcnow().isoformat()
    }
    
    logger.info(f"Webhook created: {webhook_id} - {webhook.url}")
    
    return webhooks_db[webhook_id]

@app.get("/webhooks")
async def list_webhooks():
    """List all registered webhooks"""
    webhooks_list = []
    for webhook_id, webhook in webhooks_db.items():
        # Hide secret in listing
        webhook_copy = webhook.copy()
        if 'secret' in webhook_copy:
            webhook_copy['secret'] = "***" if webhook_copy['secret'] else None
        webhooks_list.append(webhook_copy)
    
    return {"webhooks": webhooks_list, "total": len(webhooks_list)}

@app.get("/webhooks/{webhook_id}")
async def get_webhook(webhook_id: str):
    """Get a specific webhook"""
    if webhook_id not in webhooks_db:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    webhook = webhooks_db[webhook_id].copy()
    if 'secret' in webhook:
        webhook['secret'] = "***" if webhook['secret'] else None
    return webhook

@app.put("/webhooks/{webhook_id}")
async def update_webhook(webhook_id: str, webhook: Webhook):
    """Update a webhook"""
    if webhook_id not in webhooks_db:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    webhooks_db[webhook_id].update({
        "url": str(webhook.url),
        "events": webhook.events,
        "secret": webhook.secret,
        "enabled": webhook.enabled,
        "headers": webhook.headers,
        "updated_at": datetime.utcnow().isoformat()
    })
    
    logger.info(f"Webhook updated: {webhook_id}")
    
    return webhooks_db[webhook_id]

@app.delete("/webhooks/{webhook_id}")
async def delete_webhook(webhook_id: str):
    """Delete a webhook"""
    if webhook_id not in webhooks_db:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    del webhooks_db[webhook_id]
    logger.info(f"Webhook deleted: {webhook_id}")
    
    return {"status": "deleted", "webhook_id": webhook_id}

@app.post("/webhooks/{webhook_id}/test")
async def test_webhook(webhook_id: str, background_tasks: BackgroundTasks):
    """Test a webhook by sending a sample event"""
    if webhook_id not in webhooks_db:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    test_event = WebhookEvent(
        event="webhook.test",
        timestamp=datetime.utcnow().isoformat(),
        data={"message": "This is a test webhook", "webhook_id": webhook_id}
    )
    
    background_tasks.add_task(send_webhook, webhook_id, test_event)
    
    return {"status": "test_sent", "webhook_id": webhook_id}

@app.get("/webhooks/history")
async def get_webhook_history(limit: int = 50):
    """Get webhook delivery history"""
    return {
        "history": list(reversed(webhook_history))[:limit],
        "total": len(webhook_history)
    }

@app.post("/trigger")
async def manual_trigger(event_data: dict):
    """Manually trigger a webhook event"""
    event_type = event_data.get("event", "manual.trigger")
    
    event = WebhookEvent(
        event=event_type,
        timestamp=datetime.utcnow().isoformat(),
        data=event_data.get("data", {})
    )
    
    # Send to all webhooks
    sent_count = 0
    for webhook_id in webhooks_db.keys():
        await send_webhook(webhook_id, event)
        sent_count += 1
    
    return {
        "status": "triggered",
        "event": event_type,
        "webhooks_notified": sent_count
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8085"))
    uvicorn.run(app, host="0.0.0.0", port=port)

