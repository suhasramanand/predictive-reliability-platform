# Demo Guide

This guide walks through a complete demonstration of the Predictive Reliability Platform.

## Pre-Demo Setup (5 minutes)

```bash
# Navigate to project
cd predictive-reliability-platform

# Start all services
make up

# Wait for services to initialize
sleep 60

# Verify health
make health
```

## Demo Flow (15-20 minutes)

### Act 1: System Overview (3 minutes)

**Show the architecture:**
- Open README and explain component diagram
- Highlight: 3 microservices → Prometheus → Anomaly Detection → Policy Engine

**Access the Dashboard:**
```bash
open http://localhost:3000
```

**Tour the Dashboard:**
1. **Overview Tab**:
   - Show auto-remediation status (ENABLED)
   - Show service health cards (all green)
   - Show quick links to Grafana, Prometheus, Jaeger

2. **Anomalies Tab**:
   - Currently empty or minimal anomalies
   - Explain: Real-time detection with confidence scores

3. **Actions Tab**:
   - May have some historical actions
   - Explain: Complete audit trail of remediation

4. **Policies Tab**:
   - Show 9 configured policies
   - Point out different conditions and actions

### Act 2: Observability Stack (3 minutes)

**Prometheus:**
```bash
open http://localhost:9090
```
- Navigate to Status → Targets
- Show all 3 services are UP and being scraped
- Run a query: `orders_latency_seconds`
- Show graph visualization

**Grafana:**
```bash
open http://localhost:3001  # admin/admin
```
- Show pre-configured Prometheus datasource
- Navigate through available dashboards
- Explain: Real-time metrics visualization

**Jaeger:**
```bash
open http://localhost:16686
```
- Explain: Distributed tracing across services
- Will see traces once we generate traffic

### Act 3: Generate Traffic & Observe (5 minutes)

**Start Chaos Simulator:**
```bash
# In a new terminal
make chaos-load
```

**Back to Dashboard:**
- Refresh Anomalies tab
- Watch predictions appearing in real-time
- Point out: service name, metric, current value, expected range

**Switch to Grafana:**
- Show live metrics updating
- Point out request rate increasing
- Show latency graphs responding

**Check Jaeger:**
- Select service (e.g., "orders-service")
- Show distributed traces
- Click on a trace to see span details
- Explain: End-to-end request flow visibility

### Act 4: Anomaly Detection (4 minutes)

**Inject Chaos:**
```bash
# Stop previous command (Ctrl+C)
# Start aggressive chaos
make chaos
```

**Watch Anomalies Tab:**
- Anomalies should start appearing in red
- Show severity levels: warning, critical
- Point out high confidence scores (>80%)

**Explain the Detection:**
- Statistical analysis (moving average + std dev)
- Monitors: latency, error rate, CPU usage
- 30-second detection interval
- Z-score based confidence

**Check Anomaly API directly:**
```bash
curl http://localhost:8080/predict | jq
```

### Act 5: Auto-Remediation (5 minutes)

**Watch Actions Tab:**
- Refresh to see new remediation actions
- Show action details:
  - Policy name
  - Action type (restart_container)
  - Reason (with specific metric values)
  - Status (completed/failed)
  - Timestamp

**Check Docker:**
```bash
# Show container restarts
docker ps -a

# Check restart counts
docker inspect orders-service --format='{{.RestartCount}}'
```

**Verify Recovery:**
- Go back to Overview tab
- Services should return to healthy state
- Anomaly count decreasing

**Explain Policy Matching:**
```bash
# Show policy configuration
cat policy_engine/policies.yml
```
- Condition: "latency > 0.5"
- Action: "restart_container"
- Cooldown: 300 seconds (prevents spam)

### Act 6: Manual Controls (2 minutes)

**Disable Auto-Remediation:**
- Click "ENABLED" button in Overview
- Status changes to "DISABLED"
- Continue chaos injection
- Show: Anomalies detected but no actions taken

**Re-enable:**
- Click "DISABLED" button
- Watch actions resume

**Manual Triggers:**
```bash
# Trigger detection manually
curl -X POST http://localhost:8080/detect/manual | jq

# Trigger policy evaluation manually
curl -X POST http://localhost:8081/evaluate | jq
```

## Post-Demo Q&A Topics

### Technical Deep Dives

**Q: How does anomaly detection work?**
- Statistical approach: moving average ± (2.5 × std deviation)
- Configurable sensitivity and window size
- Future: ML models like LSTM, Prophet

**Q: What actions can the policy engine take?**
- Currently: restart_container, scale_up, alert
- Extensible: can add custom actions
- Docker SDK for container management
- K8s client for scaling

**Q: Is this production-ready?**
- Current: PoC/Demo quality
- For production:
  - Add authentication/authorization
  - Persistent storage (PostgreSQL, S3)
  - High availability setup
  - Kubernetes deployment
  - Monitoring of monitoring

### Architecture Questions

**Q: How does it scale?**
- Horizontal: Multiple replicas with load balancer
- Prometheus: Federation for multi-cluster
- Anomaly service: Can scale independently
- Policy engine: Leader election for HA

**Q: What about false positives?**
- Adjust sensitivity parameter
- Tune cooldown periods
- Add policy conditions (AND/OR logic)
- Machine learning for pattern learning

**Q: Integration with existing tools?**
- Prometheus: Standard metrics format
- Grafana: Can connect to any datasource
- Alert webhooks: Slack, PagerDuty
- API-first: Easy integration

## Cleanup

```bash
# Stop all services
make down

# Clean everything including volumes
make clean
```

## Troubleshooting During Demo

### Services Not Starting
```bash
# Check logs
docker-compose logs

# Restart specific service
docker-compose restart orders-service
```

### No Anomalies Detected
```bash
# Increase chaos
cd chaos_simulator
python chaos.py chaos --duration 300

# Or manually create anomaly
# (repeatedly hit service to spike metrics)
```

### Dashboard Not Loading
```bash
# Check dashboard logs
docker logs dashboard

# Restart dashboard
docker-compose restart dashboard
```

## Demo Script Variations

### Short Version (5 minutes)
1. Show architecture diagram
2. Open dashboard
3. Run `make chaos`
4. Show anomalies appearing
5. Show auto-remediation actions

### Technical Deep Dive (30 minutes)
- Include code walkthrough
- Show Prometheus queries
- Explain anomaly algorithm
- Live debugging session
- Policy creation demo

### Executive Overview (10 minutes)
- Focus on business value
- Show cost savings potential
- Discuss SRE best practices
- Demonstrate ROI metrics
- Highlight automation benefits

## Key Talking Points

1. **Proactive vs Reactive**: Detect issues before users notice
2. **Automation**: Reduce MTTR from hours to seconds
3. **Observability**: Complete visibility across stack
4. **SRE Principles**: Error budgets, blameless postmortems
5. **Cloud Native**: Container-ready, scalable architecture
6. **Open Source**: Built on industry-standard tools
7. **Extensible**: Easy to add new services, policies, actions

---

**Pro Tip**: Keep terminals ready with commands pre-typed for smooth transitions!


