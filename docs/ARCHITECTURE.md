# System Architecture

## High-Level Overview

The Predictive Reliability Platform is a cloud-native system designed to automatically detect and remediate issues in microservices environments.

## Component Interactions

```
┌─────────────────────────────────────────────────────────────────────┐
│                         User Interface Layer                         │
│                                                                       │
│  ┌──────────────────┐                    ┌──────────────────────┐   │
│  │  Dashboard UI    │                    │   Grafana Dashboards │   │
│  │  (React/TS)      │                    │   (Visualization)    │   │
│  └────────┬─────────┘                    └──────────┬───────────┘   │
└───────────┼──────────────────────────────────────────┼───────────────┘
            │                                          │
            │ HTTP/REST                                │ HTTP
            │                                          │
┌───────────┼──────────────────────────────────────────┼───────────────┐
│           │              Intelligence Layer          │               │
│           │                                          │               │
│  ┌────────▼─────────┐              ┌────────────────▼──────────┐    │
│  │ Anomaly Service  │◀────────────▶│     Prometheus            │    │
│  │ (Detection)      │  Query API   │  (Metrics Storage)        │    │
│  └────────┬─────────┘              └────────────▲──────────────┘    │
│           │                                     │                    │
│           │ Anomalies                           │ Scrape             │
│           ▼                                     │                    │
│  ┌──────────────────┐                          │                    │
│  │  Policy Engine   │                          │                    │
│  │  (Remediation)   │                          │                    │
│  └────────┬─────────┘                          │                    │
└───────────┼──────────────────────────────────────┼───────────────────┘
            │                                      │
            │ Docker API                           │
            │ (restart/scale)                      │
            │                                      │
┌───────────┼──────────────────────────────────────┼───────────────────┐
│           │              Service Layer           │                   │
│           │                                      │                   │
│  ┌────────▼─────────┐  ┌──────────────┐  ┌──────▼──────────┐        │
│  │  Orders Service  │  │Users Service │  │Payments Service │        │
│  │    (FastAPI)     │  │  (FastAPI)   │  │   (FastAPI)     │        │
│  └──────────────────┘  └──────────────┘  └─────────────────┘        │
│           │                   │                   │                  │
│           └───────────────────┴───────────────────┘                  │
│                               │                                      │
│                               ▼                                      │
│                    ┌─────────────────────┐                          │
│                    │  Jaeger (Traces)    │                          │
│                    │  Loki (Logs)        │                          │
│                    └─────────────────────┘                          │
└──────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Metrics Collection
```
Microservices → /metrics endpoint → Prometheus (scrape every 10s) → Time-series DB
```

### 2. Anomaly Detection
```
Anomaly Service → Query Prometheus API → Statistical Analysis → Detect Anomalies
                                                                         │
                                                                         ▼
                                                        Store Predictions & Anomalies
```

### 3. Policy Evaluation & Remediation
```
Policy Engine → Fetch Anomalies → Evaluate Policies → Match Condition?
                                                            │
                                                            ▼ Yes
                                                    Execute Action
                                                    (restart/scale/alert)
                                                            │
                                                            ▼
                                                    Record Action History
```

### 4. Visualization
```
Dashboard → Poll Anomaly Service API → Display Real-time Data
         → Poll Policy Engine API → Show Actions
         
User → Grafana → Query Prometheus → Display Metrics
```

## Anomaly Detection Algorithm

### Statistical Approach

The system uses a moving average and standard deviation approach:

1. **Data Collection**: Maintain sliding window of last N metric values
2. **Statistics Calculation**:
   - Mean (μ) = average of recent values
   - Standard Deviation (σ) = measure of variance
3. **Threshold Calculation**:
   - Lower bound = μ - (sensitivity × σ)
   - Upper bound = μ + (sensitivity × σ)
4. **Anomaly Detection**:
   - If current_value < lower_bound OR current_value > upper_bound
   - Then: ANOMALY
5. **Confidence Calculation**:
   - Z-score = |current_value - μ| / σ
   - Confidence = 0.5 + (z_score / 10)

### Parameters

- **window_size**: Number of historical points (default: 20)
- **sensitivity**: Standard deviation multiplier (default: 2.5)
- **check_interval**: Detection frequency (default: 30s)

## Policy Engine Logic

### Policy Structure
```yaml
- name: "policy_name"
  condition: "metric operator threshold"  # e.g., "latency > 0.5"
  action: "action_type"                   # restart_container, scale_up, alert
  service: "target_service"
  cooldown: 300                           # seconds
  enabled: true
```

### Evaluation Loop

```python
while True:
    anomalies = fetch_anomalies()
    
    for anomaly in anomalies:
        for policy in policies:
            if policy.enabled and \
               policy.service == anomaly.service and \
               evaluate_condition(policy.condition, anomaly.metric, anomaly.value) and \
               check_cooldown(policy.name):
                
                execute_action(policy.action, policy.service)
                record_action(policy, anomaly)
                set_cooldown(policy.name)
    
    sleep(check_interval)
```

## Technology Stack

### Backend Services
- **Language**: Python 3.11
- **Framework**: FastAPI (async, high-performance)
- **ASGI Server**: Uvicorn
- **HTTP Client**: Requests, Axios

### Observability
- **Metrics**: Prometheus (TSDB)
- **Logs**: Loki (log aggregation)
- **Traces**: Jaeger (distributed tracing)
- **Visualization**: Grafana

### Frontend
- **Framework**: React 18
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Build Tool**: Vite
- **Charts**: Recharts
- **Routing**: React Router

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Container Runtime**: Docker Engine
- **Networking**: Bridge networks

### Instrumentation
- **Metrics**: prometheus-client (Python)
- **Tracing**: OpenTelemetry SDK
- **Format**: Prometheus exposition format

## Security Considerations

### Current Implementation
- Services isolated in Docker network
- Read-only Docker socket mount for policy engine
- No authentication (PoC only)

### Production Recommendations
1. **Authentication & Authorization**:
   - API keys for service-to-service
   - OAuth2/OIDC for dashboard
   - RBAC for policy engine

2. **Network Security**:
   - TLS/SSL for all communication
   - Service mesh (Istio/Linkerd)
   - Network policies

3. **Secrets Management**:
   - Vault, AWS Secrets Manager
   - Encrypted environment variables

4. **Container Security**:
   - Non-root users
   - Read-only filesystems
   - Security scanning (Trivy, Snyk)

## Scalability

### Current Limitations
- In-memory storage (ephemeral)
- Single instance of each service
- No persistence across restarts

### Production Scaling
1. **Horizontal Scaling**:
   - Multiple replicas with load balancing
   - Kubernetes HPA based on metrics
   - Service mesh for traffic management

2. **Data Persistence**:
   - PostgreSQL for policy engine state
   - Redis for anomaly cache
   - S3 for long-term metric storage

3. **High Availability**:
   - Multi-zone deployment
   - Prometheus federation
   - Grafana HA setup

## Performance Characteristics

### Metrics
- **Scrape interval**: 10 seconds
- **Anomaly detection**: 30 seconds
- **Policy evaluation**: 30 seconds
- **Dashboard refresh**: 10 seconds

### Resource Usage (Approximate)
- **Total CPU**: 2-4 cores
- **Total RAM**: 4-6 GB
- **Disk**: Minimal (time-series in-memory)

### Latency
- **Service response**: < 100ms (p95)
- **Anomaly detection**: < 1s per metric
- **Policy execution**: < 2s per action
- **Dashboard load**: < 500ms

## Failure Modes & Recovery

### Service Failures
- **Microservice crash**: Auto-restart by Docker
- **Anomaly service down**: No detection, services continue
- **Policy engine down**: No remediation, manual intervention
- **Prometheus down**: No metrics collection, data gap

### Data Loss
- **Metric data**: Lost on Prometheus restart (use persistent volumes)
- **Action history**: Lost on policy engine restart
- **Predictions**: Rebuilt on anomaly service restart

### Split Brain
- Single instance architecture prevents split brain
- For HA: implement leader election (etcd, Consul)

## Monitoring the Monitor

### Health Checks
- All services expose `/health` endpoint
- Docker healthchecks configured
- Prometheus scrape success monitoring

### Meta-Monitoring
- Monitor Prometheus with external system
- Alert on anomaly service failures
- Track policy engine action success rate

## Future Architecture Enhancements

1. **Event-Driven Architecture**:
   - Kafka/RabbitMQ for event bus
   - Async policy evaluation
   - Event sourcing for audit

2. **Advanced ML**:
   - LSTM for time-series prediction
   - Prophet for seasonality
   - Clustering for pattern recognition

3. **Multi-Tenancy**:
   - Namespace isolation
   - Per-tenant policies
   - Resource quotas

4. **GitOps**:
   - Policy-as-Code in Git
   - ArgoCD/Flux deployment
   - Automated rollback

5. **Cost Optimization**:
   - Spot instance recommendations
   - Right-sizing suggestions
   - Idle resource detection


