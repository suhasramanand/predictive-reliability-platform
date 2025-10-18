# Predictive Reliability Platform - API Documentation

Complete API reference for integrating with the Predictive Reliability Platform.

## Base URLs

```
Dashboard API:      http://localhost:3000/api
Anomaly API:        http://localhost:8080
Policy API:         http://localhost:8081
AI API:             http://localhost:8090
Prometheus API:     http://localhost:9090/api/v1
Grafana API:        http://localhost:3001/api
Jaeger API:         http://localhost:16686/api
```

---

## Table of Contents

1. [Authentication](#authentication)
2. [Anomaly Detection API](#anomaly-detection-api)
3. [AI-Powered Analysis API](#ai-powered-analysis-api)
4. [Policy Engine API](#policy-engine-api)
5. [Service Health API](#service-health-api)
6. [Actions API](#actions-api)
7. [Metrics Query API](#metrics-query-api)
8. [Webhooks](#webhooks)
9. [Error Codes](#error-codes)
10. [Rate Limits](#rate-limits)

---

## Authentication

Currently, the platform runs without authentication for local development. For production:

```bash
# Add API key to requests
curl -H "Authorization: Bearer YOUR_API_KEY" \
     http://api.reliability-platform.com/anomalies
```

---

## Anomaly Detection API

Base URL: `http://localhost:8080`

### Get All Anomalies

**Endpoint:** `GET /anomalies`

Returns current anomalies detected across all services.

**Request:**
```bash
curl http://localhost:8080/anomalies
```

**Response:**
```json
{
  "anomalies": [
    {
      "id": "anomaly_1729267890",
      "service": "orders-service",
      "metric": "cpu_usage",
      "current_value": 92.5,
      "predicted_value": 45.2,
      "anomaly_score": 0.87,
      "severity": "high",
      "timestamp": "2024-10-18T14:30:00Z",
      "trend": "increasing",
      "forecast_exhaustion": "2024-10-18T16:45:00Z",
      "recommendation": "Scale up replicas or investigate high CPU process"
    },
    {
      "id": "anomaly_1729267891",
      "service": "payments-service",
      "metric": "error_rate",
      "current_value": 0.08,
      "predicted_value": 0.01,
      "anomaly_score": 0.92,
      "severity": "critical",
      "timestamp": "2024-10-18T14:32:00Z",
      "trend": "spike",
      "recommendation": "Check recent deployments and database connectivity"
    }
  ],
  "total": 2,
  "timestamp": "2024-10-18T14:35:00Z"
}
```

**Query Parameters:**
- `service` (string): Filter by service name
- `severity` (string): Filter by severity (low, medium, high, critical)
- `since` (ISO8601): Get anomalies since timestamp
- `limit` (int): Max results (default: 50)

**Examples:**
```bash
# Get anomalies for specific service
curl "http://localhost:8080/anomalies?service=orders-service"

# Get critical anomalies only
curl "http://localhost:8080/anomalies?severity=critical"

# Get anomalies from last hour
curl "http://localhost:8080/anomalies?since=2024-10-18T13:35:00Z"
```

---

### Get Anomaly by ID

**Endpoint:** `GET /anomalies/{id}`

**Request:**
```bash
curl http://localhost:8080/anomalies/anomaly_1729267890
```

**Response:**
```json
{
  "id": "anomaly_1729267890",
  "service": "orders-service",
  "metric": "cpu_usage",
  "current_value": 92.5,
  "predicted_value": 45.2,
  "anomaly_score": 0.87,
  "severity": "high",
  "timestamp": "2024-10-18T14:30:00Z",
  "details": {
    "baseline": 42.3,
    "deviation": 50.2,
    "historical_pattern": "normal_range: 35-55%",
    "similar_incidents": [
      {
        "date": "2024-10-15T10:00:00Z",
        "cause": "memory_leak",
        "resolution": "pod_restart"
      }
    ]
  },
  "related_metrics": {
    "memory_usage": 78.5,
    "disk_io": 45.2,
    "network_io": 32.1
  }
}
```

---

### Predict Future Anomalies

**Endpoint:** `POST /predict`

Forecast potential anomalies for the next time window.

**Request:**
```bash
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -d '{
    "service": "orders-service",
    "time_window": "2h",
    "metrics": ["cpu_usage", "memory_usage", "latency"]
  }'
```

**Response:**
```json
{
  "predictions": [
    {
      "metric": "cpu_usage",
      "current": 65.2,
      "predicted_1h": 78.5,
      "predicted_2h": 95.3,
      "confidence": 0.89,
      "will_breach_threshold": true,
      "estimated_breach_time": "2024-10-18T16:20:00Z",
      "recommendation": "Pre-emptive scaling recommended"
    },
    {
      "metric": "memory_usage",
      "current": 55.1,
      "predicted_1h": 60.2,
      "predicted_2h": 64.8,
      "confidence": 0.92,
      "will_breach_threshold": false
    }
  ]
}
```

---

## AI-Powered Analysis API

Base URL: `http://localhost:8090`

### Health Check

**Endpoint:** `GET /health`

**Request:**
```bash
curl http://localhost:8090/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "ai-service",
  "model": "openai/gpt-oss-120b",
  "api_provider": "groq",
  "timestamp": "2024-10-18T14:35:00Z"
}
```

---

### Chat with AI Assistant

**Endpoint:** `POST /chat`

Ask questions about your system in natural language.

**Request:**
```bash
curl -X POST http://localhost:8090/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Why is the orders service experiencing high latency?",
    "context": {
      "services": ["orders", "users", "payments"],
      "time_range": "1h"
    }
  }'
```

**Response:**
```json
{
  "answer": "## Analysis: Orders Service High Latency\n\n**Root Cause:**\nDatabase connection pool exhaustion detected.\n\n**Evidence:**\n- Connection pool: 95% utilized (baseline: 40%)\n- Query wait time: 450ms average (baseline: 25ms)\n- Active connections: 47/50 (critical)\n\n**Immediate Actions:**\n1. Restart orders-service pods to clear connections\n2. Increase connection pool size from 50 to 100\n3. Enable connection leak detection\n\n**Prevention:**\n- Review recent code changes for connection leaks\n- Add connection pool monitoring alerts\n- Implement connection timeouts (30s max)",
  "confidence": 0.91,
  "sources": ["prometheus", "loki", "jaeger"],
  "timestamp": "2024-10-18T14:35:00Z"
}
```

**Query Examples:**
```bash
# Service health check
curl -X POST http://localhost:8090/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the current health of all services?"}'

# Performance analysis
curl -X POST http://localhost:8090/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Which service has the highest error rate?"}'

# Troubleshooting
curl -X POST http://localhost:8090/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I fix the memory leak in payments service?"}'

# Capacity planning
curl -X POST http://localhost:8090/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Do we have enough capacity for Black Friday traffic?"}'
```

---

### Root Cause Analysis (RCA)

**Endpoint:** `POST /rca`

Perform automated root cause analysis for incidents.

**Request:**
```bash
curl -X POST http://localhost:8090/rca \
  -H "Content-Type: application/json" \
  -d '{
    "time_range": "1h",
    "services": ["orders", "payments"]
  }'
```

**Response:**
```json
{
  "rca": "## Root Cause Analysis\n\n### Suspected Service\npayments-service (confidence: 87%)\n\n### Confidence Level\n87%\n\n### Key Evidence\n- CPU spike from 40% to 95% at 13:45\n- Database connection errors increased 15x\n- Error rate jumped from 0.5% to 8.2%\n\n### Likely Causes\n1. Database connection pool exhaustion\n2. Query timeout cascade effect\n3. Insufficient connection pool size for load\n\n### Recommended Actions\n1. IMMEDIATE: Restart payments-service pods\n2. INVESTIGATE: Review connection pool configuration\n3. PREVENT: Increase pool size and add monitoring",
  "confidence": 0.87,
  "suspected_services": ["payments-service"],
  "correlated_events": [
    {
      "timestamp": "2024-10-18T13:45:00Z",
      "event": "cpu_spike",
      "service": "payments-service"
    },
    {
      "timestamp": "2024-10-18T13:46:00Z",
      "event": "error_rate_increase",
      "service": "payments-service"
    }
  ],
  "timestamp": "2024-10-18T14:35:00Z"
}
```

---

### Incident Summary

**Endpoint:** `POST /summarize`

Generate AI-powered incident summaries.

**Request:**
```bash
curl -X POST http://localhost:8090/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "time_range": "24h"
  }'
```

**Response:**
```json
{
  "summary": "## 24-Hour Incident Summary\n\n### Affected Services\n- payments-service: 2 incidents (high severity)\n- orders-service: 1 incident (medium severity)\n\n### Key Symptoms\n- Database connection pool exhaustion\n- CPU spikes during peak traffic\n- Elevated error rates (avg 3.2%)\n\n### Current Status\n- All services: HEALTHY\n- Auto-remediation: 2/3 incidents resolved automatically\n- Manual intervention: 1 incident required restart\n\n### Next Steps\n1. Review connection pool sizing\n2. Implement pre-emptive scaling policies\n3. Add capacity planning for peak hours",
  "incident_count": 3,
  "auto_resolved": 2,
  "manual_resolved": 1,
  "affected_services": ["payments", "orders"],
  "severity_breakdown": {
    "critical": 0,
    "high": 2,
    "medium": 1,
    "low": 0
  },
  "timestamp": "2024-10-18T14:35:00Z"
}
```

---

### Get Remediation Advice

**Endpoint:** `POST /advice`

Get AI-powered remediation recommendations.

**Request:**
```bash
curl -X POST http://localhost:8090/advice \
  -H "Content-Type: application/json" \
  -d '{
    "service": "orders-service",
    "anomaly": "high_cpu_usage",
    "context": {
      "cpu": 92.5,
      "memory": 65.2,
      "error_rate": 0.02
    }
  }'
```

**Response:**
```json
{
  "advice": "## Remediation: High CPU Usage - Orders Service\n\n### Immediate Actions (Do Now)\n1. Check for runaway processes: `kubectl top pods -l app=orders`\n2. Scale horizontally: Increase replicas from 3 to 6\n3. Enable CPU throttling if needed\n\n### Investigation Steps\n1. Profile CPU usage: Enable profiling endpoint\n2. Check for inefficient queries or loops\n3. Review recent deployments for performance regressions\n\n### Long-term Prevention\n1. Implement auto-scaling policies (CPU > 70%)\n2. Add CPU usage alerts at 80% threshold\n3. Conduct load testing before deployments\n4. Consider vertical scaling if consistent high usage",
  "priority": "high",
  "estimated_resolution_time": "15 minutes",
  "automation_available": true,
  "policy_recommendation": {
    "condition": "cpu_usage > 70",
    "action": "scale_up",
    "parameters": {
      "min_replicas": 3,
      "max_replicas": 10,
      "target_cpu": 60
    }
  }
}
```

---

## Policy Engine API

Base URL: `http://localhost:8081`

### List All Policies

**Endpoint:** `GET /policies`

**Request:**
```bash
curl http://localhost:8081/policies
```

**Response:**
```json
{
  "policies": [
    {
      "id": "policy_cpu_auto_scale",
      "name": "Auto-scale on high CPU",
      "enabled": true,
      "condition": "cpu_usage > 80 AND trend = increasing",
      "actions": [
        {
          "type": "scale",
          "parameters": {
            "min_replicas": 3,
            "max_replicas": 10,
            "scale_up_by": 2
          }
        },
        {
          "type": "alert",
          "parameters": {
            "channel": "slack",
            "message": "Auto-scaling {service} due to high CPU"
          }
        }
      ],
      "services": ["orders-service", "payments-service"],
      "created_at": "2024-10-15T10:00:00Z",
      "executions": 15,
      "success_rate": 0.93
    }
  ]
}
```

---

### Create Policy

**Endpoint:** `POST /policies`

**Request:**
```bash
curl -X POST http://localhost:8081/policies \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Memory Leak Auto-Restart",
    "condition": "memory_usage > 90 AND memory_trend = increasing",
    "actions": [
      {
        "type": "restart_pod",
        "parameters": {
          "graceful": true,
          "max_unavailable": 1
        }
      },
      {
        "type": "alert",
        "parameters": {
          "channel": "pagerduty",
          "severity": "high",
          "message": "Memory leak detected, auto-restart initiated"
        }
      }
    ],
    "services": ["*"],
    "enabled": true,
    "cooldown": "15m"
  }'
```

**Response:**
```json
{
  "id": "policy_mem_restart_001",
  "status": "created",
  "message": "Policy created successfully",
  "policy": {
    "id": "policy_mem_restart_001",
    "name": "Memory Leak Auto-Restart",
    "enabled": true,
    "condition": "memory_usage > 90 AND memory_trend = increasing",
    "actions": [...],
    "created_at": "2024-10-18T14:35:00Z"
  }
}
```

---

### Update Policy

**Endpoint:** `PUT /policies/{id}`

**Request:**
```bash
curl -X PUT http://localhost:8081/policies/policy_cpu_auto_scale \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": false,
    "condition": "cpu_usage > 85 AND trend = increasing"
  }'
```

---

### Delete Policy

**Endpoint:** `DELETE /policies/{id}`

**Request:**
```bash
curl -X DELETE http://localhost:8081/policies/policy_cpu_auto_scale
```

**Response:**
```json
{
  "status": "deleted",
  "message": "Policy policy_cpu_auto_scale deleted successfully"
}
```

---

### Test Policy (Dry Run)

**Endpoint:** `POST /policies/{id}/test`

Test a policy without executing actions.

**Request:**
```bash
curl -X POST http://localhost:8081/policies/policy_cpu_auto_scale/test \
  -H "Content-Type: application/json" \
  -d '{
    "service": "orders-service",
    "metrics": {
      "cpu_usage": 85,
      "memory_usage": 60,
      "error_rate": 0.01
    }
  }'
```

**Response:**
```json
{
  "would_trigger": true,
  "matched_conditions": ["cpu_usage > 80", "trend = increasing"],
  "actions_to_execute": [
    {
      "type": "scale",
      "service": "orders-service",
      "parameters": {"scale_to": 6}
    },
    {
      "type": "alert",
      "channel": "slack",
      "message": "Auto-scaling orders-service due to high CPU"
    }
  ],
  "estimated_execution_time": "45 seconds"
}
```

---

## Service Health API

Base URL: `http://localhost:8080`

### Get All Services Health

**Endpoint:** `GET /health`

**Request:**
```bash
curl http://localhost:8080/health
```

**Response:**
```json
{
  "services": [
    {
      "service": "orders-service",
      "status": "healthy",
      "uptime": "15d 4h 23m",
      "version": "v2.3.1",
      "replicas": {
        "desired": 3,
        "ready": 3,
        "available": 3
      },
      "metrics": {
        "cpu_usage": 45.2,
        "memory_usage": 62.8,
        "disk_usage": 35.1,
        "latency_p50": 125,
        "latency_p95": 245,
        "latency_p99": 380,
        "request_rate": 1250.5,
        "error_rate": 0.008
      },
      "last_deployment": "2024-10-15T08:00:00Z",
      "last_restart": "2024-10-15T08:02:00Z"
    },
    {
      "service": "payments-service",
      "status": "degraded",
      "uptime": "2h 15m",
      "version": "v1.8.2",
      "replicas": {
        "desired": 4,
        "ready": 3,
        "available": 3
      },
      "metrics": {
        "cpu_usage": 78.5,
        "memory_usage": 82.3,
        "error_rate": 0.045
      },
      "issues": [
        "High error rate detected",
        "1 replica unhealthy"
      ],
      "last_deployment": "2024-10-18T13:00:00Z"
    }
  ],
  "overall_status": "degraded",
  "timestamp": "2024-10-18T14:35:00Z"
}
```

---

### Get Single Service Health

**Endpoint:** `GET /health/{service}`

**Request:**
```bash
curl http://localhost:8080/health/orders-service
```

---

## Actions API

Base URL: `http://localhost:8081`

### List Available Actions

**Endpoint:** `GET /actions`

**Response:**
```json
{
  "actions": [
    {
      "type": "restart_pod",
      "description": "Restart service pods",
      "parameters": ["service", "graceful", "max_unavailable"],
      "estimated_duration": "30-60 seconds"
    },
    {
      "type": "scale",
      "description": "Scale service replicas",
      "parameters": ["service", "replicas", "min", "max"],
      "estimated_duration": "60-90 seconds"
    },
    {
      "type": "alert",
      "description": "Send alert notification",
      "parameters": ["channel", "severity", "message"],
      "estimated_duration": "instant"
    },
    {
      "type": "circuit_breaker",
      "description": "Enable/disable circuit breaker",
      "parameters": ["service", "state"],
      "estimated_duration": "instant"
    },
    {
      "type": "rate_limit",
      "description": "Adjust rate limiting",
      "parameters": ["service", "limit", "window"],
      "estimated_duration": "instant"
    }
  ]
}
```

---

### Execute Action

**Endpoint:** `POST /actions/execute`

**Request:**
```bash
curl -X POST http://localhost:8081/actions/execute \
  -H "Content-Type: application/json" \
  -d '{
    "action": "restart_pod",
    "service": "orders-service",
    "parameters": {
      "graceful": true,
      "max_unavailable": 1
    },
    "reason": "High memory usage, suspected leak",
    "initiated_by": "api_user_123"
  }'
```

**Response:**
```json
{
  "action_id": "action_1729267890",
  "status": "executing",
  "action": "restart_pod",
  "service": "orders-service",
  "started_at": "2024-10-18T14:35:00Z",
  "estimated_completion": "2024-10-18T14:36:00Z",
  "progress_url": "/actions/action_1729267890/status"
}
```

---

### Get Action Status

**Endpoint:** `GET /actions/{action_id}/status`

**Request:**
```bash
curl http://localhost:8081/actions/action_1729267890/status
```

**Response:**
```json
{
  "action_id": "action_1729267890",
  "status": "completed",
  "action": "restart_pod",
  "service": "orders-service",
  "started_at": "2024-10-18T14:35:00Z",
  "completed_at": "2024-10-18T14:35:45Z",
  "duration": "45 seconds",
  "result": {
    "success": true,
    "pods_restarted": 3,
    "downtime": "0 seconds",
    "new_pod_names": [
      "orders-service-7d8c9f-abc12",
      "orders-service-7d8c9f-def34",
      "orders-service-7d8c9f-ghi56"
    ]
  },
  "logs": [
    "14:35:00 - Initiated graceful restart",
    "14:35:05 - Draining pod orders-service-5b7a8c-xyz89",
    "14:35:15 - Pod drained successfully",
    "14:35:20 - New pod orders-service-7d8c9f-abc12 started",
    "14:35:30 - Pod healthy and receiving traffic",
    "14:35:45 - All pods restarted successfully"
  ]
}
```

---

### Action History

**Endpoint:** `GET /actions/history`

**Request:**
```bash
curl "http://localhost:8081/actions/history?service=orders-service&limit=10"
```

**Response:**
```json
{
  "actions": [
    {
      "action_id": "action_1729267890",
      "action": "restart_pod",
      "service": "orders-service",
      "status": "completed",
      "timestamp": "2024-10-18T14:35:00Z",
      "initiated_by": "policy_engine",
      "reason": "High memory usage",
      "duration": "45 seconds",
      "success": true
    },
    {
      "action_id": "action_1729264290",
      "action": "scale",
      "service": "orders-service",
      "status": "completed",
      "timestamp": "2024-10-18T13:35:00Z",
      "initiated_by": "policy_cpu_auto_scale",
      "reason": "High CPU usage detected",
      "parameters": {"from": 3, "to": 6},
      "duration": "70 seconds",
      "success": true
    }
  ],
  "total": 25,
  "page": 1,
  "per_page": 10
}
```

---

## Metrics Query API

Base URL: `http://localhost:9090/api/v1` (Prometheus-compatible)

### Query Current Metrics

**Endpoint:** `GET /query`

**Request:**
```bash
# Single metric
curl "http://localhost:9090/api/v1/query?query=cpu_usage{service='orders'}"

# Aggregated metric
curl "http://localhost:9090/api/v1/query?query=sum(rate(http_requests_total[5m]))by(service)"
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "resultType": "vector",
    "result": [
      {
        "metric": {
          "service": "orders-service"
        },
        "value": [1729267890, "45.2"]
      }
    ]
  }
}
```

---

### Query Range Metrics

**Endpoint:** `GET /query_range`

**Request:**
```bash
curl "http://localhost:9090/api/v1/query_range?query=cpu_usage{service='orders'}&start=2024-10-18T13:00:00Z&end=2024-10-18T14:00:00Z&step=60s"
```

---

## Webhooks

Configure webhooks to receive real-time notifications.

### Register Webhook

**Endpoint:** `POST /webhooks`

**Request:**
```bash
curl -X POST http://localhost:8080/webhooks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-app.com/webhooks/reliability",
    "events": ["anomaly.detected", "incident.started", "incident.resolved"],
    "secret": "your_webhook_secret",
    "enabled": true
  }'
```

**Response:**
```json
{
  "webhook_id": "webhook_abc123",
  "url": "https://your-app.com/webhooks/reliability",
  "events": ["anomaly.detected", "incident.started", "incident.resolved"],
  "enabled": true,
  "created_at": "2024-10-18T14:35:00Z"
}
```

---

### Webhook Payload Example

When an anomaly is detected, you'll receive:

```json
{
  "event": "anomaly.detected",
  "timestamp": "2024-10-18T14:35:00Z",
  "webhook_id": "webhook_abc123",
  "data": {
    "anomaly_id": "anomaly_1729267890",
    "service": "orders-service",
    "metric": "cpu_usage",
    "severity": "high",
    "current_value": 92.5,
    "threshold": 80,
    "recommendation": "Scale up replicas"
  },
  "signature": "sha256=abc123..."
}
```

---

## Error Codes

| Code | Message | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid API key |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error occurred |
| 503 | Service Unavailable | Service temporarily unavailable |

**Error Response Format:**
```json
{
  "error": {
    "code": 400,
    "message": "Invalid service name",
    "details": "Service 'invalid-service' not found in monitoring system",
    "timestamp": "2024-10-18T14:35:00Z"
  }
}
```

---

## Rate Limits

- **Default:** 1000 requests per hour per API key
- **Burst:** 100 requests per minute
- **Webhooks:** 10,000 events per hour

**Rate Limit Headers:**
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1729271490
```

---

## SDK Examples

See [SDK_EXAMPLES.md](./SDK_EXAMPLES.md) for client libraries in:
- Python
- Node.js
- Go
- Java
- curl/bash

---

## Support

- **Documentation:** https://github.com/YOUR_USERNAME/predictive-reliability-platform
- **Issues:** https://github.com/YOUR_USERNAME/predictive-reliability-platform/issues
- **Community:** Join our Slack/Discord

---

**Last Updated:** October 18, 2024  
**API Version:** v1.0.0

