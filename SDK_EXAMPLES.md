# SDK Examples - Predictive Reliability Platform

Client libraries and code examples for integrating with the platform.

## Table of Contents

1. [Python SDK](#python-sdk)
2. [Node.js/TypeScript SDK](#nodejs--typescript-sdk)
3. [Go SDK](#go-sdk)
4. [cURL Examples](#curl-examples)
5. [WebSocket Streaming](#websocket-streaming)

---

## Python SDK

### Installation

```bash
pip install reliability-platform-sdk
```

### Basic Usage

```python
from reliability_platform import ReliabilityClient

# Initialize client
client = ReliabilityClient(
    base_url="http://localhost:8080",
    ai_url="http://localhost:8090",
    api_key="your_api_key"  # optional for local
)

# Get service health
services = client.get_health()
for service in services:
    print(f"{service['service']}: {service['status']}")
    print(f"  CPU: {service['metrics']['cpu_usage']}%")
    print(f"  Memory: {service['metrics']['memory_usage']}%")

# Get anomalies
anomalies = client.get_anomalies()
for anomaly in anomalies:
    print(f"⚠️  {anomaly['service']}: {anomaly['metric']} = {anomaly['current_value']}")
    print(f"   Recommendation: {anomaly['recommendation']}")

# Chat with AI
response = client.ai.chat("What's causing high CPU in orders service?")
print(response['answer'])

# Run RCA
rca = client.ai.root_cause_analysis(time_range="1h")
print(rca['rca'])
```

---

### Advanced Python Usage

```python
from reliability_platform import ReliabilityClient, Policy, Action
import asyncio

client = ReliabilityClient(base_url="http://localhost:8080")

# Create a new policy
policy = Policy(
    name="Auto-scale on high load",
    condition="cpu_usage > 80 AND request_rate > 1000",
    actions=[
        Action.scale(min_replicas=3, max_replicas=10),
        Action.alert(channel="slack", message="Auto-scaling triggered")
    ],
    services=["orders-service", "payments-service"]
)

created_policy = client.policies.create(policy)
print(f"Policy created: {created_policy['id']}")

# Execute action
action_result = client.actions.execute(
    action="restart_pod",
    service="orders-service",
    parameters={"graceful": True},
    reason="Memory leak detected"
)

# Wait for completion
status = client.actions.wait_for_completion(action_result['action_id'])
print(f"Action completed: {status['result']}")

# Stream anomalies in real-time
async def monitor_anomalies():
    async for anomaly in client.stream_anomalies():
        print(f"New anomaly: {anomaly}")
        
        # Auto-remediate
        if anomaly['severity'] == 'critical':
            advice = client.ai.get_advice(
                service=anomaly['service'],
                anomaly=anomaly['metric']
            )
            print(f"AI Advice: {advice['advice']}")

asyncio.run(monitor_anomalies())
```

---

### Python Helper Functions

```python
from reliability_platform import ReliabilityClient
from datetime import datetime, timedelta

def check_service_health(service_name):
    """Check if a service is healthy"""
    client = ReliabilityClient()
    health = client.get_health(service=service_name)
    
    return {
        'is_healthy': health['status'] == 'healthy',
        'cpu': health['metrics']['cpu_usage'],
        'memory': health['metrics']['memory_usage'],
        'error_rate': health['metrics']['error_rate']
    }

def predict_capacity_issues(hours=24):
    """Predict capacity issues in the next N hours"""
    client = ReliabilityClient()
    predictions = client.predict(
        time_window=f"{hours}h",
        metrics=["cpu_usage", "memory_usage", "disk_usage"]
    )
    
    issues = []
    for pred in predictions['predictions']:
        if pred['will_breach_threshold']:
            issues.append({
                'metric': pred['metric'],
                'breach_time': pred['estimated_breach_time'],
                'current': pred['current'],
                'predicted': pred[f'predicted_{hours}h'],
                'recommendation': pred['recommendation']
            })
    
    return issues

def auto_scale_if_needed(service, cpu_threshold=80):
    """Auto-scale service if CPU exceeds threshold"""
    client = ReliabilityClient()
    health = client.get_health(service=service)
    
    if health['metrics']['cpu_usage'] > cpu_threshold:
        current_replicas = health['replicas']['ready']
        new_replicas = current_replicas * 2
        
        result = client.actions.execute(
            action="scale",
            service=service,
            parameters={"replicas": new_replicas}
        )
        
        return f"Scaled {service} from {current_replicas} to {new_replicas}"
    
    return f"{service} CPU is healthy ({health['metrics']['cpu_usage']}%)"

# Usage
if __name__ == "__main__":
    # Check health
    health = check_service_health("orders-service")
    print(f"Service health: {health}")
    
    # Predict issues
    issues = predict_capacity_issues(hours=4)
    if issues:
        print("⚠️  Predicted capacity issues:")
        for issue in issues:
            print(f"  - {issue['metric']} will breach at {issue['breach_time']}")
    
    # Auto-scale if needed
    result = auto_scale_if_needed("orders-service", cpu_threshold=75)
    print(result)
```

---

## Node.js / TypeScript SDK

### Installation

```bash
npm install @reliability-platform/sdk
# or
yarn add @reliability-platform/sdk
```

### TypeScript Usage

```typescript
import { ReliabilityClient, Policy, Action } from '@reliability-platform/sdk';

// Initialize client
const client = new ReliabilityClient({
  baseUrl: 'http://localhost:8080',
  aiUrl: 'http://localhost:8090',
  apiKey: process.env.RELIABILITY_API_KEY
});

// Get service health
async function checkHealth() {
  const services = await client.health.getAll();
  
  services.forEach(service => {
    console.log(`${service.service}: ${service.status}`);
    console.log(`  CPU: ${service.metrics.cpu_usage}%`);
    console.log(`  Memory: ${service.metrics.memory_usage}%`);
  });
}

// Get anomalies
async function getAnomalies() {
  const anomalies = await client.anomalies.getAll({
    severity: 'high'
  });
  
  for (const anomaly of anomalies) {
    console.log(`⚠️  ${anomaly.service}: ${anomaly.metric}`);
    console.log(`   Current: ${anomaly.current_value}`);
    console.log(`   Expected: ${anomaly.predicted_value}`);
    console.log(`   Action: ${anomaly.recommendation}`);
  }
}

// Chat with AI
async function askAI(question: string) {
  const response = await client.ai.chat({
    query: question,
    context: {
      services: ['orders', 'payments', 'users']
    }
  });
  
  console.log('AI Response:', response.answer);
  return response;
}

// Create policy
async function createAutoScalePolicy() {
  const policy = new Policy({
    name: 'Auto-scale on high CPU',
    condition: 'cpu_usage > 80 AND trend = increasing',
    actions: [
      Action.scale({ minReplicas: 3, maxReplicas: 10 }),
      Action.alert({ channel: 'slack', message: 'Auto-scaling triggered' })
    ],
    services: ['orders-service']
  });
  
  const created = await client.policies.create(policy);
  console.log('Policy created:', created.id);
}

// Execute action with progress tracking
async function restartService(serviceName: string) {
  const action = await client.actions.execute({
    action: 'restart_pod',
    service: serviceName,
    parameters: { graceful: true },
    reason: 'Scheduled restart for memory leak fix'
  });
  
  console.log(`Action ${action.action_id} started`);
  
  // Poll for status
  const status = await client.actions.waitForCompletion(action.action_id, {
    timeout: 120000, // 2 minutes
    pollInterval: 5000 // 5 seconds
  });
  
  if (status.result.success) {
    console.log('✓ Service restarted successfully');
    console.log(`  Downtime: ${status.result.downtime}`);
  } else {
    console.error('✗ Restart failed:', status.error);
  }
}

// Real-time monitoring
async function monitorInRealTime() {
  // Subscribe to anomaly events
  client.events.on('anomaly.detected', async (anomaly) => {
    console.log('🚨 New anomaly detected:', anomaly);
    
    // Get AI recommendations
    const advice = await client.ai.getAdvice({
      service: anomaly.service,
      anomaly: anomaly.metric
    });
    
    console.log('💡 AI Recommendation:', advice.advice);
    
    // Auto-remediate if critical
    if (anomaly.severity === 'critical' && advice.automation_available) {
      console.log('🤖 Auto-remediating...');
      await client.actions.execute(advice.policy_recommendation);
    }
  });
  
  // Start listening
  await client.events.connect();
}

// Run examples
(async () => {
  await checkHealth();
  await getAnomalies();
  await askAI('What services are experiencing issues?');
  await restartService('orders-service');
  await monitorInRealTime();
})();
```

---

### React Hook Example

```typescript
// useReliability.ts
import { useState, useEffect } from 'react';
import { ReliabilityClient } from '@reliability-platform/sdk';

const client = new ReliabilityClient({
  baseUrl: process.env.REACT_APP_API_URL
});

export function useServiceHealth(serviceName: string) {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    async function fetchHealth() {
      try {
        const data = await client.health.get(serviceName);
        setHealth(data);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    }
    
    fetchHealth();
    const interval = setInterval(fetchHealth, 30000); // Refresh every 30s
    
    return () => clearInterval(interval);
  }, [serviceName]);
  
  return { health, loading, error };
}

export function useAnomalies(filters = {}) {
  const [anomalies, setAnomalies] = useState([]);
  
  useEffect(() => {
    const subscription = client.anomalies.subscribe(filters, (newAnomalies) => {
      setAnomalies(newAnomalies);
    });
    
    return () => subscription.unsubscribe();
  }, [filters]);
  
  return anomalies;
}

export function useAIChat() {
  const [loading, setLoading] = useState(false);
  
  const chat = async (query: string) => {
    setLoading(true);
    try {
      const response = await client.ai.chat({ query });
      return response.answer;
    } finally {
      setLoading(false);
    }
  };
  
  return { chat, loading };
}

// Component usage
function ServiceDashboard({ serviceName }) {
  const { health, loading } = useServiceHealth(serviceName);
  const anomalies = useAnomalies({ service: serviceName });
  const { chat } = useAIChat();
  
  if (loading) return <div>Loading...</div>;
  
  return (
    <div>
      <h2>{serviceName}</h2>
      <div>Status: {health.status}</div>
      <div>CPU: {health.metrics.cpu_usage}%</div>
      
      {anomalies.length > 0 && (
        <div>
          <h3>Anomalies</h3>
          {anomalies.map(anomaly => (
            <div key={anomaly.id}>{anomaly.recommendation}</div>
          ))}
        </div>
      )}
      
      <button onClick={() => chat(`Analyze ${serviceName} health`)}>
        Ask AI
      </button>
    </div>
  );
}
```

---

## Go SDK

### Installation

```bash
go get github.com/YOUR_USERNAME/reliability-platform-go
```

### Go Usage

```go
package main

import (
    "context"
    "fmt"
    "log"
    "time"
    
    reliability "github.com/YOUR_USERNAME/reliability-platform-go"
)

func main() {
    // Initialize client
    client := reliability.NewClient(&reliability.Config{
        BaseURL: "http://localhost:8080",
        AIURL:   "http://localhost:8090",
        APIKey:  "your_api_key",
    })
    
    ctx := context.Background()
    
    // Get service health
    services, err := client.Health.GetAll(ctx)
    if err != nil {
        log.Fatal(err)
    }
    
    for _, service := range services {
        fmt.Printf("%s: %s\n", service.Service, service.Status)
        fmt.Printf("  CPU: %.1f%%\n", service.Metrics.CPUUsage)
        fmt.Printf("  Memory: %.1f%%\n", service.Metrics.MemoryUsage)
    }
    
    // Get anomalies
    anomalies, err := client.Anomalies.GetAll(ctx, &reliability.AnomalyFilter{
        Severity: "high",
    })
    if err != nil {
        log.Fatal(err)
    }
    
    for _, anomaly := range anomalies {
        fmt.Printf("⚠️  %s: %s = %.2f\n", 
            anomaly.Service, 
            anomaly.Metric, 
            anomaly.CurrentValue)
        fmt.Printf("   %s\n", anomaly.Recommendation)
    }
    
    // Chat with AI
    response, err := client.AI.Chat(ctx, &reliability.ChatRequest{
        Query: "What's causing high latency?",
        Context: map[string]interface{}{
            "services": []string{"orders", "payments"},
        },
    })
    if err != nil {
        log.Fatal(err)
    }
    fmt.Println("AI:", response.Answer)
    
    // Create policy
    policy := &reliability.Policy{
        Name:      "Auto-scale on high CPU",
        Condition: "cpu_usage > 80",
        Actions: []reliability.Action{
            {
                Type: "scale",
                Parameters: map[string]interface{}{
                    "min_replicas": 3,
                    "max_replicas": 10,
                },
            },
        },
        Services: []string{"orders-service"},
    }
    
    created, err := client.Policies.Create(ctx, policy)
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("Policy created: %s\n", created.ID)
    
    // Execute action
    action, err := client.Actions.Execute(ctx, &reliability.ActionRequest{
        Action:  "restart_pod",
        Service: "orders-service",
        Parameters: map[string]interface{}{
            "graceful": true,
        },
        Reason: "Memory leak detected",
    })
    if err != nil {
        log.Fatal(err)
    }
    
    // Wait for completion
    status, err := client.Actions.WaitForCompletion(ctx, action.ActionID, 2*time.Minute)
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("Action completed: %+v\n", status.Result)
    
    // Real-time monitoring
    anomalyChan := make(chan *reliability.Anomaly)
    go client.Anomalies.Stream(ctx, anomalyChan)
    
    for anomaly := range anomalyChan {
        fmt.Printf("New anomaly: %s - %s\n", anomaly.Service, anomaly.Metric)
        
        // Auto-remediate
        if anomaly.Severity == "critical" {
            advice, _ := client.AI.GetAdvice(ctx, &reliability.AdviceRequest{
                Service: anomaly.Service,
                Anomaly: anomaly.Metric,
            })
            fmt.Printf("AI Advice: %s\n", advice.Advice)
        }
    }
}
```

---

## cURL Examples

### Complete Workflow

```bash
#!/bin/bash

API_URL="http://localhost:8080"
AI_URL="http://localhost:8090"
POLICY_URL="http://localhost:8081"

# 1. Check service health
echo "=== Service Health ==="
curl -s "$API_URL/health" | jq '.services[] | {service, status, cpu: .metrics.cpu_usage}'

# 2. Get current anomalies
echo "\n=== Current Anomalies ==="
curl -s "$API_URL/anomalies" | jq '.anomalies[] | {service, metric, severity, recommendation}'

# 3. Ask AI about issues
echo "\n=== AI Analysis ==="
curl -s -X POST "$AI_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What services are experiencing problems?",
    "context": {"services": ["orders", "payments", "users"]}
  }' | jq -r '.answer'

# 4. Run RCA
echo "\n=== Root Cause Analysis ==="
curl -s -X POST "$AI_URL/rca" \
  -H "Content-Type: application/json" \
  -d '{"time_range": "1h"}' | jq -r '.rca'

# 5. Create auto-remediation policy
echo "\n=== Creating Policy ==="
POLICY_ID=$(curl -s -X POST "$POLICY_URL/policies" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Auto-restart on high memory",
    "condition": "memory_usage > 90",
    "actions": [
      {
        "type": "restart_pod",
        "parameters": {"graceful": true}
      }
    ],
    "services": ["*"]
  }' | jq -r '.id')

echo "Policy created: $POLICY_ID"

# 6. Execute manual action
echo "\n=== Executing Action ==="
ACTION_ID=$(curl -s -X POST "$POLICY_URL/actions/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "scale",
    "service": "orders-service",
    "parameters": {"replicas": 5},
    "reason": "Anticipated traffic spike"
  }' | jq -r '.action_id')

echo "Action started: $ACTION_ID"

# 7. Monitor action progress
echo "\n=== Monitoring Action ==="
while true; do
  STATUS=$(curl -s "$POLICY_URL/actions/$ACTION_ID/status" | jq -r '.status')
  echo "Status: $STATUS"
  
  if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then
    curl -s "$POLICY_URL/actions/$ACTION_ID/status" | jq '.result'
    break
  fi
  
  sleep 5
done

# 8. Get predictions
echo "\n=== Capacity Predictions ==="
curl -s -X POST "$API_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "service": "orders-service",
    "time_window": "2h",
    "metrics": ["cpu_usage", "memory_usage"]
  }' | jq '.predictions[] | {metric, current, predicted_2h, will_breach_threshold}'

# 9. Get action history
echo "\n=== Recent Actions ==="
curl -s "$POLICY_URL/actions/history?limit=5" | jq '.actions[] | {action, service, status, duration}'
```

---

## WebSocket Streaming

### Real-time Anomaly Stream

```javascript
// JavaScript/Node.js
const WebSocket = require('ws');

const ws = new WebSocket('ws://localhost:8080/stream/anomalies');

ws.on('open', () => {
  console.log('Connected to anomaly stream');
  
  // Subscribe to specific services
  ws.send(JSON.stringify({
    action: 'subscribe',
    filters: {
      services: ['orders-service', 'payments-service'],
      severity: ['high', 'critical']
    }
  }));
});

ws.on('message', (data) => {
  const anomaly = JSON.parse(data);
  console.log('New anomaly:', anomaly);
  
  // Handle anomaly
  if (anomaly.severity === 'critical') {
    handleCriticalAnomaly(anomaly);
  }
});

ws.on('error', (error) => {
  console.error('WebSocket error:', error);
});

function handleCriticalAnomaly(anomaly) {
  // Auto-remediate or alert
  console.log(`🚨 Critical: ${anomaly.service} - ${anomaly.metric}`);
}
```

---

### Python WebSocket Client

```python
import asyncio
import websockets
import json

async def stream_anomalies():
    uri = "ws://localhost:8080/stream/anomalies"
    
    async with websockets.connect(uri) as websocket:
        # Subscribe
        await websocket.send(json.dumps({
            "action": "subscribe",
            "filters": {
                "services": ["orders-service"],
                "severity": ["high", "critical"]
            }
        }))
        
        # Listen for anomalies
        async for message in websocket:
            anomaly = json.loads(message)
            print(f"🚨 Anomaly: {anomaly['service']} - {anomaly['metric']}")
            
            # Auto-remediate
            if anomaly['severity'] == 'critical':
                await handle_critical_anomaly(anomaly)

async def handle_critical_anomaly(anomaly):
    # Execute remediation action
    print(f"Auto-remediating: {anomaly['recommendation']}")

asyncio.run(stream_anomalies())
```

---

## Integration Examples

### CI/CD Pipeline (GitHub Actions)

```yaml
- name: Check Reliability Before Deploy
  run: |
    # Check for anomalies
    ANOMALIES=$(curl -s http://reliability-platform/anomalies | jq -r '.anomalies | length')
    
    if [ "$ANOMALIES" -gt 0 ]; then
      echo "⚠️  Anomalies detected, aborting deploy"
      curl -s http://reliability-platform/anomalies | jq '.anomalies'
      exit 1
    fi
    
    # Predict capacity issues
    ISSUES=$(curl -s -X POST http://reliability-platform/predict \
      -d '{"service":"app","time_window":"4h"}' | \
      jq -r '.predictions[] | select(.will_breach_threshold == true) | .metric' | wc -l)
    
    if [ "$ISSUES" -gt 0 ]; then
      echo "⚠️  Capacity issues predicted in next 4 hours"
      exit 1
    fi
    
    echo "✅ All checks passed, proceeding with deploy"
```

---

### Slack Bot Integration

```python
from slack_sdk import WebClient
from reliability_platform import ReliabilityClient

slack = WebClient(token="xoxb-your-token")
reliability = ReliabilityClient()

@slack.event("app_mention")
def handle_mention(event):
    text = event['text']
    channel = event['channel']
    
    # Ask AI
    if "status" in text.lower():
        services = reliability.get_health()
        message = "📊 Service Status:\n"
        for svc in services:
            emoji = "✅" if svc['status'] == 'healthy' else "⚠️"
            message += f"{emoji} {svc['service']}: {svc['status']}\n"
        
        slack.chat_postMessage(channel=channel, text=message)
    
    elif "anomalies" in text.lower():
        anomalies = reliability.get_anomalies()
        if anomalies:
            message = "🚨 Current Anomalies:\n"
            for anomaly in anomalies:
                message += f"• {anomaly['service']}: {anomaly['recommendation']}\n"
        else:
            message = "✅ No anomalies detected"
        
        slack.chat_postMessage(channel=channel, text=message)
    
    else:
        # Ask AI
        response = reliability.ai.chat(text)
        slack.chat_postMessage(channel=channel, text=response['answer'])
```

---

## Support

For more examples and support:
- GitHub: https://github.com/YOUR_USERNAME/predictive-reliability-platform
- Documentation: See API_DOCUMENTATION.md
- Issues: Open an issue on GitHub

---

**Last Updated:** October 18, 2024

