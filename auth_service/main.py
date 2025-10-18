"""
Authentication & API Key Management Service
Handles API key generation, validation, and rate limiting
"""
import os
import secrets
import hashlib
import time
from datetime import datetime, timedelta
from typing import Optional, Dict
from fastapi import FastAPI, HTTPException, Security, Depends, Header
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from collections import defaultdict
import json

app = FastAPI(title="Authentication Service", version="1.0.0")

# Configuration
API_KEYS_FILE = os.getenv("API_KEYS_FILE", "/app/data/api_keys.json")
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "1000"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1 hour

# In-memory storage (should be Redis in production)
api_keys_db: Dict[str, dict] = {}
rate_limit_tracker = defaultdict(list)

# Security
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

class APIKey(BaseModel):
    name: str
    description: str = ""
    scopes: list[str] = ["read", "write"]

class APIKeyResponse(BaseModel):
    key: str
    name: str
    created_at: str
    scopes: list[str]
    
class RateLimitInfo(BaseModel):
    limit: int
    remaining: int
    reset_at: str

def load_api_keys():
    """Load API keys from file"""
    global api_keys_db
    try:
        if os.path.exists(API_KEYS_FILE):
            with open(API_KEYS_FILE, 'r') as f:
                api_keys_db = json.load(f)
    except Exception as e:
        print(f"Error loading API keys: {e}")
        api_keys_db = {}

def save_api_keys():
    """Save API keys to file"""
    try:
        os.makedirs(os.path.dirname(API_KEYS_FILE), exist_ok=True)
        with open(API_KEYS_FILE, 'w') as f:
            json.dump(api_keys_db, f, indent=2)
    except Exception as e:
        print(f"Error saving API keys: {e}")

def hash_key(key: str) -> str:
    """Hash API key for storage"""
    return hashlib.sha256(key.encode()).hexdigest()

def generate_api_key() -> str:
    """Generate a new API key"""
    return f"rp_{secrets.token_urlsafe(32)}"

def check_rate_limit(api_key: str) -> tuple[bool, RateLimitInfo]:
    """Check if API key has exceeded rate limit"""
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW
    
    # Clean old requests
    rate_limit_tracker[api_key] = [
        req_time for req_time in rate_limit_tracker[api_key]
        if req_time > window_start
    ]
    
    # Check limit
    request_count = len(rate_limit_tracker[api_key])
    remaining = max(0, RATE_LIMIT_REQUESTS - request_count)
    reset_at = datetime.fromtimestamp(now + RATE_LIMIT_WINDOW).isoformat()
    
    rate_info = RateLimitInfo(
        limit=RATE_LIMIT_REQUESTS,
        remaining=remaining,
        reset_at=reset_at
    )
    
    if request_count >= RATE_LIMIT_REQUESTS:
        return False, rate_info
    
    # Record this request
    rate_limit_tracker[api_key].append(now)
    
    return True, rate_info

async def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> dict:
    """Verify API key and check rate limits"""
    # Allow health checks without auth
    if api_key is None:
        raise HTTPException(status_code=401, detail="API key required")
    
    # Verify key exists
    key_hash = hash_key(api_key)
    if key_hash not in api_keys_db:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Check rate limit
    allowed, rate_info = check_rate_limit(key_hash)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Resets at {rate_info.reset_at}",
            headers={
                "X-RateLimit-Limit": str(rate_info.limit),
                "X-RateLimit-Remaining": str(rate_info.remaining),
                "X-RateLimit-Reset": rate_info.reset_at
            }
        )
    
    return {
        **api_keys_db[key_hash],
        "rate_limit": rate_info.dict()
    }

@app.on_event("startup")
async def startup():
    """Load API keys on startup"""
    load_api_keys()
    
    # Create default admin key if none exist
    if not api_keys_db:
        admin_key = generate_api_key()
        admin_hash = hash_key(admin_key)
        api_keys_db[admin_hash] = {
            "name": "admin",
            "description": "Default admin key - auto-generated",
            "scopes": ["read", "write", "admin"],
            "created_at": datetime.utcnow().isoformat()
            # NEVER store the original key - security risk!
        }
        save_api_keys()
        print(f"")
        print(f"╔═══════════════════════════════════════════════════════════════╗")
        print(f"║  ⚠️  ADMIN API KEY GENERATED - SAVE THIS SECURELY!           ║")
        print(f"╚═══════════════════════════════════════════════════════════════╝")
        print(f"")
        print(f"   API Key: {admin_key}")
        print(f"")
        print(f"   This key will NOT be shown again!")
        print(f"   Store it in a password manager or secure location.")
        print(f"")
        print(f"   Use this key to create additional API keys via:")
        print(f"   POST /keys with X-API-Key header")
        print(f"")

@app.get("/health")
async def health():
    """Health check (no auth required)"""
    return {"status": "healthy", "service": "auth-service"}

@app.post("/keys", response_model=APIKeyResponse)
async def create_api_key(
    key_config: APIKey,
    auth: dict = Depends(verify_api_key)
):
    """Create a new API key (admin only)"""
    if "admin" not in auth.get("scopes", []):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Generate new key
    new_key = generate_api_key()
    key_hash = hash_key(new_key)
    
    # Store metadata
    api_keys_db[key_hash] = {
        "name": key_config.name,
        "description": key_config.description,
        "scopes": key_config.scopes,
        "created_at": datetime.utcnow().isoformat()
    }
    save_api_keys()
    
    return APIKeyResponse(
        key=new_key,
        name=key_config.name,
        created_at=api_keys_db[key_hash]["created_at"],
        scopes=key_config.scopes
    )

@app.get("/keys")
async def list_api_keys(auth: dict = Depends(verify_api_key)):
    """List all API keys (without revealing the actual keys)"""
    if "admin" not in auth.get("scopes", []):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    keys_list = []
    for key_hash, metadata in api_keys_db.items():
        keys_list.append({
            "key_hash": key_hash[:16] + "...",
            "name": metadata["name"],
            "description": metadata.get("description", ""),
            "scopes": metadata["scopes"],
            "created_at": metadata["created_at"]
        })
    
    return {"keys": keys_list, "total": len(keys_list)}

@app.delete("/keys/{key_hash}")
async def revoke_api_key(key_hash: str, auth: dict = Depends(verify_api_key)):
    """Revoke an API key"""
    if "admin" not in auth.get("scopes", []):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if key_hash in api_keys_db:
        del api_keys_db[key_hash]
        save_api_keys()
        return {"status": "revoked", "key_hash": key_hash}
    
    raise HTTPException(status_code=404, detail="API key not found")

@app.post("/validate")
async def validate_key(x_api_key: Optional[str] = Header(None)):
    """Validate an API key and return rate limit info"""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    key_hash = hash_key(x_api_key)
    if key_hash not in api_keys_db:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    allowed, rate_info = check_rate_limit(key_hash)
    
    return {
        "valid": True,
        "name": api_keys_db[key_hash]["name"],
        "scopes": api_keys_db[key_hash]["scopes"],
        "rate_limit": rate_info.dict(),
        "allowed": allowed
    }

@app.get("/rate-limit/{key_hash}")
async def get_rate_limit(key_hash: str):
    """Get rate limit info for a key"""
    if key_hash not in api_keys_db:
        raise HTTPException(status_code=404, detail="API key not found")
    
    allowed, rate_info = check_rate_limit(key_hash)
    return rate_info

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8089"))
    uvicorn.run(app, host="0.0.0.0", port=port)

