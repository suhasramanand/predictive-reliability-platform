"""
Anomaly Detection Service
Uses time-series analysis to detect anomalies in service metrics
"""
import os
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import numpy as np
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import requests
from collections import defaultdict, deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Anomaly Detection Service", version="1.0.0")

# Configuration
PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://prometheus:9090")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "30"))  # seconds

# Anomaly detection state
metric_history = defaultdict(lambda: deque(maxlen=100))
anomalies = []
predictions = {}

class AnomalyPrediction(BaseModel):
    service: str
    metric: str
    current_value: float
    expected_range: Dict[str, float]
    anomaly: bool
    confidence: float
    timestamp: str
    severity: str

class AnomalyResponse(BaseModel):
    anomalies: List[AnomalyPrediction]
    count: int

class ServiceHealth(BaseModel):
    service: str
    status: str
    metrics: Dict[str, float]
    anomalies_detected: int

# Simple statistical anomaly detection
class SimpleAnomalyDetector:
    """Uses moving average and standard deviation for anomaly detection"""
    
    def __init__(self, window_size=20, sensitivity=2.5):
        self.window_size = window_size
        self.sensitivity = sensitivity
    
    def detect(self, values: List[float], current_value: float) -> tuple[bool, float, dict]:
        """
        Detect if current value is anomalous
        Returns: (is_anomaly, confidence, expected_range)
        """
        if len(values) < 5:
            return False, 0.0, {"min": 0, "max": 0, "mean": 0}
        
        # Calculate statistics
        recent_values = list(values)[-self.window_size:]
        mean = np.mean(recent_values)
        std = np.std(recent_values)
        
        if std == 0:
            std = mean * 0.1 if mean > 0 else 1.0
        
        # Define expected range
        expected_min = mean - self.sensitivity * std
        expected_max = mean + self.sensitivity * std
        
        # Check for anomaly
        is_anomaly = current_value < expected_min or current_value > expected_max
        
        # Calculate confidence
        if is_anomaly:
            z_score = abs((current_value - mean) / std) if std > 0 else 0
            confidence = min(0.95, 0.5 + (z_score / 10))
        else:
            confidence = 0.0
        
        expected_range = {
            "min": float(expected_min),
            "max": float(expected_max),
            "mean": float(mean)
        }
        
        return is_anomaly, confidence, expected_range

detector = SimpleAnomalyDetector()

def query_prometheus(query: str) -> Optional[List[Dict]]:
    """Query Prometheus API"""
    try:
        response = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={"query": query},
            timeout=5
        )
        response.raise_for_status()
        result = response.json()
        
        if result["status"] == "success" and result["data"]["result"]:
            return result["data"]["result"]
        return None
    except Exception as e:
        logger.error(f"Error querying Prometheus: {e}")
        return None

def analyze_metric(service: str, metric_name: str, query: str) -> Optional[AnomalyPrediction]:
    """Analyze a specific metric for anomalies"""
    results = query_prometheus(query)
    
    if not results:
        return None
    
    try:
        current_value = float(results[0]["value"][1])
        metric_key = f"{service}_{metric_name}"
        
        # Store historical data
        metric_history[metric_key].append(current_value)
        
        # Detect anomaly
        is_anomaly, confidence, expected_range = detector.detect(
            list(metric_history[metric_key]),
            current_value
        )
        
        # Determine severity
        if not is_anomaly:
            severity = "normal"
        elif confidence > 0.8:
            severity = "critical"
        elif confidence > 0.6:
            severity = "warning"
        else:
            severity = "info"
        
        prediction = AnomalyPrediction(
            service=service,
            metric=metric_name,
            current_value=current_value,
            expected_range=expected_range,
            anomaly=is_anomaly,
            confidence=confidence,
            timestamp=datetime.utcnow().isoformat(),
            severity=severity
        )
        
        # Store prediction
        predictions[metric_key] = prediction
        
        if is_anomaly:
            logger.warning(
                f"ANOMALY DETECTED: {service}.{metric_name} = {current_value:.2f} "
                f"(expected: {expected_range['min']:.2f}-{expected_range['max']:.2f}), "
                f"confidence: {confidence:.2f}, severity: {severity}"
            )
        
        return prediction
        
    except Exception as e:
        logger.error(f"Error analyzing metric {service}.{metric_name}: {e}")
        return None

async def run_anomaly_detection():
    """Background task to continuously check for anomalies"""
    logger.info("Starting anomaly detection background task")
    
    # Metrics to monitor
    metrics_config = [
        ("orders", "latency", 'orders_latency_seconds{quantile="0.99"}'),
        ("orders", "error_rate", 'rate(orders_errors_total[1m])'),
        ("orders", "cpu_usage", 'orders_cpu_usage_percent'),
        ("users", "latency", 'users_latency_seconds{quantile="0.99"}'),
        ("users", "error_rate", 'rate(users_errors_total[1m])'),
        ("users", "cpu_usage", 'users_cpu_usage_percent'),
        ("payments", "latency", 'payments_latency_seconds{quantile="0.99"}'),
        ("payments", "error_rate", 'rate(payments_errors_total[1m])'),
        ("payments", "cpu_usage", 'payments_cpu_usage_percent'),
    ]
    
    while True:
        try:
            global anomalies
            current_anomalies = []
            
            for service, metric_name, query in metrics_config:
                prediction = analyze_metric(service, metric_name, query)
                if prediction and prediction.anomaly:
                    current_anomalies.append(prediction)
            
            anomalies = current_anomalies
            
        except Exception as e:
            logger.error(f"Error in anomaly detection loop: {e}")
        
        await asyncio.sleep(CHECK_INTERVAL)

@app.on_event("startup")
async def startup_event():
    """Start background tasks"""
    asyncio.create_task(run_anomaly_detection())
    logger.info("Anomaly Detection Service started")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "anomaly-detection"}

@app.get("/predict", response_model=AnomalyResponse)
async def get_predictions():
    """Get current anomaly predictions"""
    return AnomalyResponse(
        anomalies=anomalies,
        count=len(anomalies)
    )

@app.get("/predictions/all")
async def get_all_predictions():
    """Get all predictions (including normal)"""
    return {
        "predictions": list(predictions.values()),
        "count": len(predictions)
    }

@app.get("/predictions/{service}")
async def get_service_predictions(service: str):
    """Get predictions for a specific service"""
    service_predictions = [
        p for p in predictions.values() if p.service == service
    ]
    return {
        "service": service,
        "predictions": service_predictions,
        "count": len(service_predictions)
    }

@app.get("/services/health")
async def get_services_health():
    """Get health status of all services"""
    services = ["orders", "users", "payments"]
    health_status = []
    
    for service in services:
        service_predictions = [
            p for p in predictions.values() if p.service == service
        ]
        
        anomaly_count = sum(1 for p in service_predictions if p.anomaly)
        
        # Determine overall status
        if anomaly_count == 0:
            status = "healthy"
        elif any(p.severity == "critical" for p in service_predictions if p.anomaly):
            status = "critical"
        elif any(p.severity == "warning" for p in service_predictions if p.anomaly):
            status = "degraded"
        else:
            status = "warning"
        
        # Extract current metrics
        metrics = {
            p.metric: p.current_value 
            for p in service_predictions
        }
        
        health_status.append(ServiceHealth(
            service=service,
            status=status,
            metrics=metrics,
            anomalies_detected=anomaly_count
        ))
    
    return {"services": health_status}

@app.post("/detect/manual")
async def manual_detection():
    """Manually trigger anomaly detection"""
    logger.info("Manual anomaly detection triggered")
    
    metrics_config = [
        ("orders", "latency", 'orders_latency_seconds{quantile="0.99"}'),
        ("orders", "error_rate", 'rate(orders_errors_total[1m])'),
        ("users", "latency", 'users_latency_seconds{quantile="0.99"}'),
        ("users", "error_rate", 'rate(users_errors_total[1m])'),
        ("payments", "latency", 'payments_latency_seconds{quantile="0.99"}'),
        ("payments", "error_rate", 'rate(payments_errors_total[1m])'),
    ]
    
    global anomalies
    current_anomalies = []
    
    for service, metric_name, query in metrics_config:
        prediction = analyze_metric(service, metric_name, query)
        if prediction and prediction.anomaly:
            current_anomalies.append(prediction)
    
    anomalies = current_anomalies
    
    return AnomalyResponse(
        anomalies=anomalies,
        count=len(anomalies)
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)


