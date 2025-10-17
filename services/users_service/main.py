"""
Users Microservice
Manages user accounts with built-in observability and failure simulation
"""
import os
import time
import random
import logging
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, EmailStr
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenTelemetry
resource = Resource.create({"service.name": "users-service"})
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

# Configure Jaeger exporter
jaeger_exporter = JaegerExporter(
    agent_host_name=os.getenv("JAEGER_AGENT_HOST", "jaeger"),
    agent_port=int(os.getenv("JAEGER_AGENT_PORT", "6831")),
)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(jaeger_exporter))

# Prometheus metrics
user_counter = Counter('users_total', 'Total number of users')
user_errors = Counter('users_errors_total', 'Total number of user errors')
user_latency = Histogram('users_latency_seconds', 'User operation latency')
active_users = Gauge('users_active', 'Number of active users')
cpu_usage = Gauge('users_cpu_usage_percent', 'Simulated CPU usage')

# FastAPI app
app = FastAPI(title="Users Service", version="1.0.0")
FastAPIInstrumentor.instrument_app(app)

# In-memory storage
users_db: Dict[str, dict] = {}

class User(BaseModel):
    name: str
    email: EmailStr
    role: str = "user"

class UserResponse(BaseModel):
    user_id: str
    name: str
    email: str
    role: str
    status: str

# Chaos flags
CHAOS_ENABLED = os.getenv("CHAOS_ENABLED", "false").lower() == "true"
FAILURE_RATE = float(os.getenv("FAILURE_RATE", "0.08"))
LATENCY_SPIKE_RATE = float(os.getenv("LATENCY_SPIKE_RATE", "0.12"))

def simulate_chaos():
    """Randomly inject failures or latency"""
    if not CHAOS_ENABLED:
        return
    
    if random.random() < FAILURE_RATE:
        logger.error("CHAOS: Simulating service failure")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    
    if random.random() < LATENCY_SPIKE_RATE:
        delay = random.uniform(0.3, 1.5)
        logger.warning(f"CHAOS: Simulating latency spike of {delay:.2f}s")
        time.sleep(delay)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "users"}

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    cpu_usage.set(random.uniform(15, 88))
    active_users.set(len([u for u in users_db.values() if u["status"] == "active"]))
    
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/users", response_model=UserResponse)
async def create_user(user: User):
    """Create a new user"""
    with tracer.start_as_current_span("create_user") as span:
        start_time = time.time()
        
        try:
            simulate_chaos()
            
            user_id = f"USR-{int(time.time() * 1000)}-{random.randint(1000, 9999)}"
            
            span.set_attribute("user.id", user_id)
            span.set_attribute("user.email", user.email)
            span.set_attribute("user.role", user.role)
            
            # Check for duplicate email
            if any(u["email"] == user.email for u in users_db.values()):
                raise HTTPException(status_code=409, detail="User with this email already exists")
            
            users_db[user_id] = {
                "user_id": user_id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "status": "active"
            }
            
            user_counter.inc()
            logger.info(f"User created: {user_id}")
            
            return UserResponse(**users_db[user_id])
            
        except HTTPException:
            user_errors.inc()
            raise
        except Exception as e:
            user_errors.inc()
            logger.error(f"Error creating user: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            user_latency.observe(time.time() - start_time)

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get user by ID"""
    with tracer.start_as_current_span("get_user") as span:
        start_time = time.time()
        
        try:
            simulate_chaos()
            
            span.set_attribute("user.id", user_id)
            
            if user_id not in users_db:
                raise HTTPException(status_code=404, detail="User not found")
            
            return UserResponse(**users_db[user_id])
            
        except HTTPException:
            user_errors.inc()
            raise
        finally:
            user_latency.observe(time.time() - start_time)

@app.get("/users")
async def list_users():
    """List all users"""
    with tracer.start_as_current_span("list_users"):
        simulate_chaos()
        return {"users": list(users_db.values()), "count": len(users_db)}

@app.put("/users/{user_id}/deactivate")
async def deactivate_user(user_id: str):
    """Deactivate user account"""
    with tracer.start_as_current_span("deactivate_user"):
        simulate_chaos()
        
        if user_id not in users_db:
            raise HTTPException(status_code=404, detail="User not found")
        
        users_db[user_id]["status"] = "inactive"
        logger.info(f"User deactivated: {user_id}")
        
        return {"message": "User deactivated", "user_id": user_id}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8002"))
    uvicorn.run(app, host="0.0.0.0", port=port)


