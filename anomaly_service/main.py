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
import pandas as pd
from fastapi import FastAPI, BackgroundTasks, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import requests
from collections import defaultdict, deque
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from prophet import Prophet
import json

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

# WebSocket connections
active_connections: List[WebSocket] = []

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

# ML-based anomaly detection
class MLAnomalyDetector:
    """Uses Isolation Forest for ML-based anomaly detection"""
    
    def __init__(self, contamination=0.1):
        self.model = IsolationForest(contamination=contamination, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.min_training_samples = 50
    
    def train(self, historical_data: np.ndarray):
        """Train the model on historical data"""
        if len(historical_data) < self.min_training_samples:
            return False
        
        try:
            # Scale features
            scaled_data = self.scaler.fit_transform(historical_data.reshape(-1, 1))
            
            # Train model
            self.model.fit(scaled_data)
            self.is_trained = True
            logger.info(f"ML model trained on {len(historical_data)} samples")
            return True
        except Exception as e:
            logger.error(f"Error training ML model: {e}")
            return False
    
    def detect(self, values: List[float], current_value: float) -> tuple[bool, float, dict]:
        """Detect anomalies using trained ML model"""
        # Train if not trained yet and enough data
        if not self.is_trained and len(values) >= self.min_training_samples:
            self.train(np.array(values))
        
        # Fall back to statistics if not trained
        if not self.is_trained:
            return False, 0.0, {"min": 0, "max": 0, "mean": 0, "method": "insufficient_data"}
        
        try:
            # Predict
            scaled_value = self.scaler.transform(np.array([[current_value]]))
            prediction = self.model.predict(scaled_value)[0]
            anomaly_score = self.model.score_samples(scaled_value)[0]
            
            is_anomaly = (prediction == -1)
            confidence = min(0.95, abs(anomaly_score) / 10) if is_anomaly else 0.0
            
            # Calculate expected range from training data
            mean = np.mean(values[-20:])
            std = np.std(values[-20:])
            
            return is_anomaly, confidence, {
                "min": float(mean - 2 * std),
                "max": float(mean + 2 * std),
                "mean": float(mean),
                "method": "isolation_forest",
                "anomaly_score": float(anomaly_score)
            }
        except Exception as e:
            logger.error(f"Error in ML detection: {e}")
            return False, 0.0, {"method": "error"}

# Time-series forecasting
class TimeSeriesForecaster:
    """Uses Prophet for time-series forecasting"""
    
    def __init__(self):
        self.models = {}  # One model per metric
        self.min_training_samples = 100
    
    def forecast(self, metric_key: str, historical_data: List[tuple], periods=24) -> Optional[dict]:
        """
        Forecast future values
        historical_data: List of (timestamp, value) tuples
        periods: Number of hours to forecast ahead
        """
        if len(historical_data) < self.min_training_samples:
            return None
        
        try:
            # Prepare data for Prophet
            df = pd.DataFrame(historical_data, columns=['ds', 'y'])
            df['ds'] = pd.to_datetime(df['ds'])
            
            # Train model
            model = Prophet(
                daily_seasonality=True,
                weekly_seasonality=False,
                yearly_seasonality=False,
                interval_width=0.95
            )
            model.fit(df)
            
            # Forecast
            future = model.make_future_dataframe(periods=periods, freq='H')
            forecast = model.predict(future)
            
            # Get predictions for future periods
            future_predictions = forecast.tail(periods)
            
            # Check if any forecasted value will breach threshold
            max_forecasted = future_predictions['yhat'].max()
            will_breach = max_forecasted > (df['y'].mean() + 2 * df['y'].std())
            
            if will_breach:
                breach_time = future_predictions[
                    future_predictions['yhat'] > (df['y'].mean() + 2 * df['y'].std())
                ]['ds'].iloc[0] if len(future_predictions[future_predictions['yhat'] > (df['y'].mean() + 2 * df['y'].std())]) > 0 else None
            else:
                breach_time = None
            
            return {
                "metric": metric_key,
                "current": float(df['y'].iloc[-1]),
                "forecasted_max": float(max_forecasted),
                "will_breach": will_breach,
                "breach_time": breach_time.isoformat() if breach_time else None,
                "forecast_horizon": f"{periods}h",
                "confidence": 0.85,
                "method": "prophet"
            }
        except Exception as e:
            logger.error(f"Error forecasting {metric_key}: {e}")
            return None

# Initialize detectors
detector = SimpleAnomalyDetector()
ml_detector = MLAnomalyDetector()
forecaster = TimeSeriesForecaster()

# Toggle for ML vs statistical
USE_ML_DETECTION = os.getenv("USE_ML_DETECTION", "false").lower() == "true"

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
        
        # Choose detector based on configuration
        if USE_ML_DETECTION:
            is_anomaly, confidence, expected_range = ml_detector.detect(
                list(metric_history[metric_key]),
                current_value
            )
            detection_method = expected_range.get('method', 'ml')
        else:
            is_anomaly, confidence, expected_range = detector.detect(
                list(metric_history[metric_key]),
                current_value
            )
            detection_method = 'statistical'
        
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
            metric=f"{metric_name} ({detection_method})",
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

@app.get("/anomalies", response_model=AnomalyResponse)
async def get_anomalies(
    service: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 50
):
    """Get current anomalies with filtering"""
    filtered = anomalies
    
    # Filter by service
    if service:
        filtered = [a for a in filtered if a.service == service]
    
    # Filter by severity
    if severity:
        filtered = [a for a in filtered if a.severity == severity]
    
    # Apply limit
    filtered = filtered[:limit]
    
    return AnomalyResponse(
        anomalies=filtered,
        count=len(filtered)
    )

@app.get("/predict", response_model=AnomalyResponse)
async def get_predictions():
    """Get current anomaly predictions (legacy endpoint)"""
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

@app.post("/forecast")
async def forecast_metrics(request: dict):
    """Forecast future metric values using Prophet"""
    service = request.get("service")
    metric_name = request.get("metric", "cpu_usage")
    periods = request.get("periods", 24)  # hours
    
    if not service:
        raise HTTPException(status_code=400, detail="service is required")
    
    metric_key = f"{service}_{metric_name}"
    
    # Get historical data with timestamps
    historical_data = []
    if metric_key in metric_history:
        history = list(metric_history[metric_key])
        # Create timestamps (assuming 30s intervals)
        base_time = datetime.utcnow() - timedelta(seconds=len(history) * 30)
        for i, value in enumerate(history):
            ts = base_time + timedelta(seconds=i * 30)
            historical_data.append((ts, value))
    
    if not historical_data:
        return {
            "error": "No historical data available for forecasting",
            "service": service,
            "metric": metric_name
        }
    
    # Forecast
    forecast_result = forecaster.forecast(metric_key, historical_data, periods=periods)
    
    if forecast_result:
        return forecast_result
    else:
        return {
            "error": "Insufficient data for forecasting (need 100+ data points)",
            "service": service,
            "metric": metric_name,
            "data_points": len(historical_data)
        }

@app.post("/ml/toggle")
async def toggle_ml_detection():
    """Toggle between ML and statistical detection"""
    global USE_ML_DETECTION
    USE_ML_DETECTION = not USE_ML_DETECTION
    logger.info(f"Detection method: {'ML (Isolation Forest)' if USE_ML_DETECTION else 'Statistical (Z-score)'}")
    return {
        "ml_enabled": USE_ML_DETECTION,
        "method": "isolation_forest" if USE_ML_DETECTION else "statistical"
    }

@app.get("/ml/status")
async def get_ml_status():
    """Get ML model status"""
    return {
        "ml_enabled": USE_ML_DETECTION,
        "ml_model_trained": ml_detector.is_trained,
        "detection_method": "isolation_forest" if USE_ML_DETECTION else "statistical",
        "training_samples_required": ml_detector.min_training_samples,
        "forecasting_available": True,
        "forecasting_samples_required": forecaster.min_training_samples
    }

@app.websocket("/stream/anomalies")
async def websocket_anomalies(websocket: WebSocket):
    """WebSocket endpoint for streaming anomalies in real-time"""
    await websocket.accept()
    active_connections.append(websocket)
    logger.info(f"WebSocket client connected. Total connections: {len(active_connections)}")
    
    try:
        # Send initial anomalies
        await websocket.send_json({
            "event": "connected",
            "anomalies": [a.dict() for a in anomalies],
            "timestamp": datetime.utcnow().isoformat()
        })
        
        last_sent_anomalies = set()
        
        # Stream updates
        while True:
            # Send new anomalies
            current_anomaly_ids = set()
            for anomaly in anomalies:
                anomaly_id = f"{anomaly.service}_{anomaly.metric}_{anomaly.timestamp}"
                current_anomaly_ids.add(anomaly_id)
                
                if anomaly_id not in last_sent_anomalies:
                    await websocket.send_json({
                        "event": "anomaly.detected",
                        "anomaly": anomaly.dict(),
                        "timestamp": datetime.utcnow().isoformat()
                    })
            
            last_sent_anomalies = current_anomaly_ids
            
            # Wait before next update
            await asyncio.sleep(5)
            
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)
        logger.info(f"Client removed. Total connections: {len(active_connections)}")

@app.get("/stream/status")
async def get_stream_status():
    """Get streaming status"""
    return {
        "active_connections": len(active_connections),
        "websocket_url": "ws://localhost:8080/stream/anomalies",
        "supported_events": ["connected", "anomaly.detected"]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)


