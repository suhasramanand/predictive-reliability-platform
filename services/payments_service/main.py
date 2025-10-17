"""
Payments Microservice
Processes payments with built-in observability and failure simulation
"""
import os
import time
import random
import logging
from typing import Dict
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
resource = Resource.create({"service.name": "payments-service"})
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

# Configure Jaeger exporter
jaeger_exporter = JaegerExporter(
    agent_host_name=os.getenv("JAEGER_AGENT_HOST", "jaeger"),
    agent_port=int(os.getenv("JAEGER_AGENT_PORT", "6831")),
)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(jaeger_exporter))

# Prometheus metrics
payment_counter = Counter('payments_total', 'Total number of payments')
payment_errors = Counter('payments_errors_total', 'Total number of payment errors')
payment_latency = Histogram('payments_latency_seconds', 'Payment processing latency')
payment_amount = Histogram('payments_amount_dollars', 'Payment amounts')
failed_payments = Counter('payments_failed_total', 'Total failed payments')
cpu_usage = Gauge('payments_cpu_usage_percent', 'Simulated CPU usage')

# FastAPI app
app = FastAPI(title="Payments Service", version="1.0.0")
FastAPIInstrumentor.instrument_app(app)

# In-memory storage
payments_db: Dict[str, dict] = {}

class Payment(BaseModel):
    order_id: str
    amount: float
    payment_method: str

class PaymentResponse(BaseModel):
    payment_id: str
    order_id: str
    amount: float
    payment_method: str
    status: str

# Chaos flags
CHAOS_ENABLED = os.getenv("CHAOS_ENABLED", "false").lower() == "true"
FAILURE_RATE = float(os.getenv("FAILURE_RATE", "0.12"))
LATENCY_SPIKE_RATE = float(os.getenv("LATENCY_SPIKE_RATE", "0.20"))

def simulate_chaos():
    """Randomly inject failures or latency"""
    if not CHAOS_ENABLED:
        return
    
    if random.random() < FAILURE_RATE:
        logger.error("CHAOS: Simulating payment gateway failure")
        raise HTTPException(status_code=502, detail="Payment gateway unavailable")
    
    if random.random() < LATENCY_SPIKE_RATE:
        delay = random.uniform(0.8, 3.0)
        logger.warning(f"CHAOS: Simulating latency spike of {delay:.2f}s")
        time.sleep(delay)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "payments"}

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    cpu_usage.set(random.uniform(30, 92))
    
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/payments", response_model=PaymentResponse)
async def process_payment(payment: Payment):
    """Process a payment"""
    with tracer.start_as_current_span("process_payment") as span:
        start_time = time.time()
        
        try:
            simulate_chaos()
            
            payment_id = f"PAY-{int(time.time() * 1000)}-{random.randint(1000, 9999)}"
            
            span.set_attribute("payment.id", payment_id)
            span.set_attribute("payment.order_id", payment.order_id)
            span.set_attribute("payment.amount", payment.amount)
            span.set_attribute("payment.method", payment.payment_method)
            
            # Simulate payment processing
            time.sleep(random.uniform(0.1, 0.3))
            
            # Random payment failures
            if CHAOS_ENABLED and random.random() < 0.05:
                status = "failed"
                failed_payments.inc()
                logger.error(f"Payment failed: {payment_id}")
            else:
                status = "completed"
                logger.info(f"Payment processed: {payment_id}")
            
            payments_db[payment_id] = {
                "payment_id": payment_id,
                "order_id": payment.order_id,
                "amount": payment.amount,
                "payment_method": payment.payment_method,
                "status": status
            }
            
            payment_counter.inc()
            payment_amount.observe(payment.amount)
            
            return PaymentResponse(**payments_db[payment_id])
            
        except HTTPException:
            payment_errors.inc()
            failed_payments.inc()
            raise
        except Exception as e:
            payment_errors.inc()
            failed_payments.inc()
            logger.error(f"Error processing payment: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            payment_latency.observe(time.time() - start_time)

@app.get("/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: str):
    """Get payment by ID"""
    with tracer.start_as_current_span("get_payment") as span:
        start_time = time.time()
        
        try:
            simulate_chaos()
            
            span.set_attribute("payment.id", payment_id)
            
            if payment_id not in payments_db:
                raise HTTPException(status_code=404, detail="Payment not found")
            
            return PaymentResponse(**payments_db[payment_id])
            
        except HTTPException:
            payment_errors.inc()
            raise
        finally:
            payment_latency.observe(time.time() - start_time)

@app.get("/payments")
async def list_payments():
    """List all payments"""
    with tracer.start_as_current_span("list_payments"):
        simulate_chaos()
        return {"payments": list(payments_db.values()), "count": len(payments_db)}

@app.post("/payments/{payment_id}/refund")
async def refund_payment(payment_id: str):
    """Refund a payment"""
    with tracer.start_as_current_span("refund_payment"):
        simulate_chaos()
        
        if payment_id not in payments_db:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        if payments_db[payment_id]["status"] != "completed":
            raise HTTPException(status_code=400, detail="Can only refund completed payments")
        
        payments_db[payment_id]["status"] = "refunded"
        logger.info(f"Payment refunded: {payment_id}")
        
        return {"message": "Payment refunded", "payment_id": payment_id}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8003"))
    uvicorn.run(app, host="0.0.0.0", port=port)


