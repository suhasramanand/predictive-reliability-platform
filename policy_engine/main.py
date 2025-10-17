"""
Policy & Auto-Remediation Engine
Evaluates policies and executes remediation actions
"""
import os
import yaml
import logging
import asyncio
from datetime import datetime
from typing import List, Dict, Optional
import docker
import requests
from fastapi import FastAPI
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Policy Engine", version="1.0.0")

# Configuration
ANOMALY_SERVICE_URL = os.getenv("ANOMALY_SERVICE_URL", "http://anomaly-service:8080")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "30"))
AUTO_REMEDIATION_ENABLED = os.getenv("AUTO_REMEDIATION_ENABLED", "true").lower() == "true"

# Docker client
try:
    docker_client = docker.from_env()
    logger.info("Docker client initialized successfully")
except Exception as e:
    logger.warning(f"Docker client initialization failed: {e}")
    docker_client = None

# Action history
action_history = []

class Policy(BaseModel):
    name: str
    condition: str
    action: str
    service: str
    cooldown: int = 300  # seconds
    enabled: bool = True

class RemediationAction(BaseModel):
    action_id: str
    policy_name: str
    service: str
    action: str
    reason: str
    status: str
    timestamp: str
    details: Optional[str] = None

class PolicyStatus(BaseModel):
    auto_remediation_enabled: bool
    policies_loaded: int
    actions_executed: int
    last_check: Optional[str]

# Load policies
def load_policies() -> List[Policy]:
    """Load policies from YAML file"""
    policies_file = "/app/policies.yml"
    
    if not os.path.exists(policies_file):
        logger.warning(f"Policies file not found: {policies_file}")
        return get_default_policies()
    
    try:
        with open(policies_file, 'r') as f:
            data = yaml.safe_load(f)
            policies = [Policy(**p) for p in data.get('policies', [])]
            logger.info(f"Loaded {len(policies)} policies from {policies_file}")
            return policies
    except Exception as e:
        logger.error(f"Error loading policies: {e}")
        return get_default_policies()

def get_default_policies() -> List[Policy]:
    """Return default policies"""
    return [
        Policy(
            name="high_latency_restart",
            condition="latency > 0.5",
            action="restart_container",
            service="orders",
            cooldown=300
        ),
        Policy(
            name="high_cpu_alert",
            condition="cpu_usage > 85",
            action="alert",
            service="orders",
            cooldown=180
        ),
        Policy(
            name="high_error_rate_restart",
            condition="error_rate > 0.1",
            action="restart_container",
            service="payments",
            cooldown=300
        ),
        Policy(
            name="users_latency_restart",
            condition="latency > 0.5",
            action="restart_container",
            service="users",
            cooldown=300
        ),
    ]

policies = load_policies()
last_action_time = {}

def evaluate_condition(condition: str, metric_name: str, value: float) -> bool:
    """Evaluate a policy condition"""
    try:
        # Parse condition: "metric operator threshold"
        parts = condition.split()
        if len(parts) != 3:
            return False
        
        cond_metric, operator, threshold = parts
        threshold = float(threshold)
        
        # Check if this condition applies to the current metric
        if cond_metric not in metric_name:
            return False
        
        # Evaluate condition
        if operator == '>':
            return value > threshold
        elif operator == '<':
            return value < threshold
        elif operator == '>=':
            return value >= threshold
        elif operator == '<=':
            return value <= threshold
        elif operator == '==':
            return value == threshold
        
        return False
    except Exception as e:
        logger.error(f"Error evaluating condition '{condition}': {e}")
        return False

def check_cooldown(policy_name: str, cooldown: int) -> bool:
    """Check if policy is in cooldown period"""
    if policy_name not in last_action_time:
        return True
    
    elapsed = (datetime.utcnow() - last_action_time[policy_name]).total_seconds()
    return elapsed >= cooldown

def restart_container(service_name: str) -> tuple[bool, str]:
    """Restart a Docker container"""
    if not docker_client:
        return False, "Docker client not available"
    
    try:
        # Find container by service name
        containers = docker_client.containers.list(
            filters={"name": service_name}
        )
        
        if not containers:
            return False, f"Container {service_name} not found"
        
        container = containers[0]
        container.restart(timeout=10)
        
        logger.info(f"Restarted container: {service_name}")
        return True, f"Container {service_name} restarted successfully"
        
    except Exception as e:
        logger.error(f"Error restarting container {service_name}: {e}")
        return False, str(e)

def scale_service(service_name: str, replicas: int = 2) -> tuple[bool, str]:
    """Scale service (placeholder for Kubernetes)"""
    # In Docker Compose, scaling is limited
    # This would be implemented for Kubernetes using kubectl or client library
    logger.info(f"Scale action requested for {service_name} to {replicas} replicas")
    return True, f"Scaling {service_name} to {replicas} replicas (simulated)"

def send_alert(service_name: str, reason: str) -> tuple[bool, str]:
    """Send alert (log for now, could integrate with Slack/email)"""
    alert_msg = f"ALERT: {service_name} - {reason}"
    logger.warning(alert_msg)
    # TODO: Integrate with Slack/email/PagerDuty
    return True, "Alert sent (logged)"

def execute_action(policy: Policy, reason: str) -> RemediationAction:
    """Execute a remediation action"""
    action_id = f"ACTION-{int(datetime.utcnow().timestamp() * 1000)}"
    
    logger.info(
        f"Executing action: {policy.action} for service {policy.service} "
        f"(policy: {policy.name}, reason: {reason})"
    )
    
    # Execute the action
    success = False
    details = ""
    
    if policy.action == "restart_container":
        success, details = restart_container(policy.service)
    elif policy.action == "scale_up":
        success, details = scale_service(policy.service, replicas=2)
    elif policy.action == "alert":
        success, details = send_alert(policy.service, reason)
    else:
        details = f"Unknown action: {policy.action}"
    
    status = "completed" if success else "failed"
    
    # Record action
    action = RemediationAction(
        action_id=action_id,
        policy_name=policy.name,
        service=policy.service,
        action=policy.action,
        reason=reason,
        status=status,
        timestamp=datetime.utcnow().isoformat(),
        details=details
    )
    
    action_history.append(action)
    last_action_time[policy.name] = datetime.utcnow()
    
    # Keep only last 100 actions
    if len(action_history) > 100:
        action_history.pop(0)
    
    return action

def get_anomalies() -> List[Dict]:
    """Fetch anomalies from anomaly detection service"""
    try:
        response = requests.get(
            f"{ANOMALY_SERVICE_URL}/predict",
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        return data.get("anomalies", [])
    except Exception as e:
        logger.error(f"Error fetching anomalies: {e}")
        return []

async def policy_evaluation_loop():
    """Background task to continuously evaluate policies"""
    logger.info("Starting policy evaluation loop")
    
    while True:
        try:
            if not AUTO_REMEDIATION_ENABLED:
                logger.debug("Auto-remediation is disabled")
                await asyncio.sleep(CHECK_INTERVAL)
                continue
            
            # Get current anomalies
            anomalies = get_anomalies()
            
            if not anomalies:
                logger.debug("No anomalies detected")
                await asyncio.sleep(CHECK_INTERVAL)
                continue
            
            logger.info(f"Evaluating {len(anomalies)} anomalies against {len(policies)} policies")
            
            # Evaluate each anomaly against policies
            for anomaly in anomalies:
                service = anomaly.get("service")
                metric = anomaly.get("metric")
                value = anomaly.get("current_value")
                
                for policy in policies:
                    if not policy.enabled:
                        continue
                    
                    # Check if policy applies to this service
                    if policy.service != service:
                        continue
                    
                    # Check if condition matches
                    if not evaluate_condition(policy.condition, metric, value):
                        continue
                    
                    # Check cooldown
                    if not check_cooldown(policy.name, policy.cooldown):
                        logger.debug(f"Policy {policy.name} is in cooldown")
                        continue
                    
                    # Execute action
                    reason = (
                        f"{service}.{metric} = {value:.2f} "
                        f"(anomaly detected with confidence {anomaly.get('confidence', 0):.2f})"
                    )
                    execute_action(policy, reason)
            
        except Exception as e:
            logger.error(f"Error in policy evaluation loop: {e}")
        
        await asyncio.sleep(CHECK_INTERVAL)

@app.on_event("startup")
async def startup_event():
    """Start background tasks"""
    asyncio.create_task(policy_evaluation_loop())
    logger.info("Policy Engine started")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "policy-engine"}

@app.get("/status", response_model=PolicyStatus)
async def get_status():
    """Get policy engine status"""
    return PolicyStatus(
        auto_remediation_enabled=AUTO_REMEDIATION_ENABLED,
        policies_loaded=len(policies),
        actions_executed=len(action_history),
        last_check=datetime.utcnow().isoformat()
    )

@app.get("/policies")
async def get_policies():
    """Get all policies"""
    return {"policies": policies, "count": len(policies)}

@app.get("/actions")
async def get_actions():
    """Get action history"""
    return {"actions": action_history, "count": len(action_history)}

@app.get("/actions/recent")
async def get_recent_actions(limit: int = 10):
    """Get recent actions"""
    recent = action_history[-limit:] if len(action_history) > limit else action_history
    return {"actions": list(reversed(recent)), "count": len(recent)}

@app.post("/evaluate")
async def manual_evaluation():
    """Manually trigger policy evaluation"""
    logger.info("Manual policy evaluation triggered")
    
    if not AUTO_REMEDIATION_ENABLED:
        return {"message": "Auto-remediation is disabled", "actions": []}
    
    anomalies = get_anomalies()
    actions_taken = []
    
    for anomaly in anomalies:
        service = anomaly.get("service")
        metric = anomaly.get("metric")
        value = anomaly.get("current_value")
        
        for policy in policies:
            if not policy.enabled:
                continue
            
            if policy.service != service:
                continue
            
            if not evaluate_condition(policy.condition, metric, value):
                continue
            
            if not check_cooldown(policy.name, policy.cooldown):
                continue
            
            reason = f"{service}.{metric} = {value:.2f}"
            action = execute_action(policy, reason)
            actions_taken.append(action)
    
    return {"message": "Evaluation complete", "actions": actions_taken}

@app.post("/toggle")
async def toggle_auto_remediation():
    """Toggle auto-remediation on/off"""
    global AUTO_REMEDIATION_ENABLED
    AUTO_REMEDIATION_ENABLED = not AUTO_REMEDIATION_ENABLED
    logger.info(f"Auto-remediation {'enabled' if AUTO_REMEDIATION_ENABLED else 'disabled'}")
    return {"auto_remediation_enabled": AUTO_REMEDIATION_ENABLED}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8081"))
    uvicorn.run(app, host="0.0.0.0", port=port)


