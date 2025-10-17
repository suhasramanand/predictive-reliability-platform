"""
Orders Microservice
Provides order management with built-in observability and failure simulation
"""
import os
import time
import random
import logging
from typing import Dict, List
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
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
resource = Resource.create({"service.name": "orders-service"})
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

# Configure Jaeger exporter
jaeger_exporter = JaegerExporter(
    agent_host_name=os.getenv("JAEGER_AGENT_HOST", "jaeger"),
    agent_port=int(os.getenv("JAEGER_AGENT_PORT", "6831")),
)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(jaeger_exporter))

# Prometheus metrics
order_counter = Counter('orders_total', 'Total number of orders')
order_errors = Counter('orders_errors_total', 'Total number of order errors')
order_latency = Histogram('orders_latency_seconds', 'Order processing latency')
active_orders = Gauge('orders_active', 'Number of active orders')
cpu_usage = Gauge('orders_cpu_usage_percent', 'Simulated CPU usage')

# FastAPI app
app = FastAPI(title="Orders Service", version="1.0.0")
FastAPIInstrumentor.instrument_app(app)

# In-memory storage
orders_db: Dict[str, dict] = {}

class Order(BaseModel):
    customer_id: str
    items: List[str]
    total: float

class OrderResponse(BaseModel):
    order_id: str
    customer_id: str
    items: List[str]
    total: float
    status: str

# Chaos flags
CHAOS_ENABLED = os.getenv("CHAOS_ENABLED", "false").lower() == "true"
FAILURE_RATE = float(os.getenv("FAILURE_RATE", "0.1"))
LATENCY_SPIKE_RATE = float(os.getenv("LATENCY_SPIKE_RATE", "0.15"))

def simulate_chaos():
    """Randomly inject failures or latency"""
    if not CHAOS_ENABLED:
        return
    
    # Random failures
    if random.random() < FAILURE_RATE:
        logger.error("CHAOS: Simulating service failure")
        raise HTTPException(status_code=500, detail="Simulated service failure")
    
    # Random latency spikes
    if random.random() < LATENCY_SPIKE_RATE:
        delay = random.uniform(0.5, 2.0)
        logger.warning(f"CHAOS: Simulating latency spike of {delay:.2f}s")
        time.sleep(delay)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "orders"}

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    # Simulate CPU usage variations
    cpu_usage.set(random.uniform(20, 95))
    active_orders.set(len(orders_db))
    
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/orders", response_model=OrderResponse)
async def create_order(order: Order):
    """Create a new order"""
    with tracer.start_as_current_span("create_order") as span:
        start_time = time.time()
        
        try:
            simulate_chaos()
            
            order_id = f"ORD-{int(time.time() * 1000)}-{random.randint(1000, 9999)}"
            
            span.set_attribute("order.id", order_id)
            span.set_attribute("order.customer_id", order.customer_id)
            span.set_attribute("order.total", order.total)
            
            orders_db[order_id] = {
                "order_id": order_id,
                "customer_id": order.customer_id,
                "items": order.items,
                "total": order.total,
                "status": "pending"
            }
            
            order_counter.inc()
            logger.info(f"Order created: {order_id}")
            
            return OrderResponse(**orders_db[order_id])
            
        except HTTPException:
            order_errors.inc()
            raise
        except Exception as e:
            order_errors.inc()
            logger.error(f"Error creating order: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            order_latency.observe(time.time() - start_time)

@app.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str):
    """Get order by ID"""
    with tracer.start_as_current_span("get_order") as span:
        start_time = time.time()
        
        try:
            simulate_chaos()
            
            span.set_attribute("order.id", order_id)
            
            if order_id not in orders_db:
                raise HTTPException(status_code=404, detail="Order not found")
            
            return OrderResponse(**orders_db[order_id])
            
        except HTTPException:
            order_errors.inc()
            raise
        finally:
            order_latency.observe(time.time() - start_time)

@app.get("/orders")
async def list_orders():
    """List all orders"""
    with tracer.start_as_current_span("list_orders"):
        simulate_chaos()
        return {"orders": list(orders_db.values()), "count": len(orders_db)}

@app.put("/orders/{order_id}/complete")
async def complete_order(order_id: str):
    """Mark order as complete"""
    with tracer.start_as_current_span("complete_order"):
        simulate_chaos()
        
        if order_id not in orders_db:
            raise HTTPException(status_code=404, detail="Order not found")
        
        orders_db[order_id]["status"] = "completed"
        logger.info(f"Order completed: {order_id}")
        
        return {"message": "Order completed", "order_id": order_id}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port)


