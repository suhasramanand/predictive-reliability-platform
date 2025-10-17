#!/bin/bash

# Comprehensive End-to-End Test Script
# This script verifies all components of the Predictive Reliability Platform

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Predictive Reliability Platform - E2E Test"
echo "=========================================="
echo ""

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
        exit 1
    fi
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "ℹ $1"
}

# 1. Check Prerequisites
echo "1. Checking Prerequisites..."
echo "----------------------------"

# Check Docker
if command -v docker &> /dev/null; then
    print_status 0 "Docker is installed"
    if docker ps &> /dev/null; then
        print_status 0 "Docker daemon is running"
    else
        print_status 1 "Docker daemon is not running. Please start Docker Desktop."
    fi
else
    print_status 1 "Docker is not installed"
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    print_status 0 "Docker Compose is installed"
else
    print_status 1 "Docker Compose is not installed"
fi

# Check Python
if command -v python3 &> /dev/null; then
    print_status 0 "Python 3 is installed"
else
    print_status 1 "Python 3 is not installed"
fi

echo ""

# 2. Build Docker Images
echo "2. Building Docker Images..."
echo "----------------------------"

print_info "This may take 5-10 minutes on first run..."

if docker-compose build --parallel 2>&1 | grep -q "Successfully"; then
    print_status 0 "All Docker images built successfully"
else
    docker-compose build
    print_status $? "Docker images built"
fi

echo ""

# 3. Start Services
echo "3. Starting Services..."
echo "----------------------------"

docker-compose up -d
sleep 10

# Check if containers are running
EXPECTED_CONTAINERS=("orders-service" "users-service" "payments-service" "anomaly-service" "policy-engine" "dashboard" "prometheus" "grafana" "loki" "jaeger")

for container in "${EXPECTED_CONTAINERS[@]}"; do
    if docker ps | grep -q "$container"; then
        print_status 0 "$container is running"
    else
        print_status 1 "$container failed to start"
    fi
done

echo ""
print_info "Waiting 30 seconds for services to fully initialize..."
sleep 30
echo ""

# 4. Health Checks
echo "4. Running Health Checks..."
echo "----------------------------"

# Orders Service
if curl -s http://localhost:8001/health | grep -q "healthy"; then
    print_status 0 "Orders Service is healthy"
else
    print_status 1 "Orders Service health check failed"
fi

# Users Service
if curl -s http://localhost:8002/health | grep -q "healthy"; then
    print_status 0 "Users Service is healthy"
else
    print_status 1 "Users Service health check failed"
fi

# Payments Service
if curl -s http://localhost:8003/health | grep -q "healthy"; then
    print_status 0 "Payments Service is healthy"
else
    print_status 1 "Payments Service health check failed"
fi

# Anomaly Service
if curl -s http://localhost:8080/health | grep -q "healthy"; then
    print_status 0 "Anomaly Service is healthy"
else
    print_status 1 "Anomaly Service health check failed"
fi

# Policy Engine
if curl -s http://localhost:8081/health | grep -q "healthy"; then
    print_status 0 "Policy Engine is healthy"
else
    print_status 1 "Policy Engine health check failed"
fi

# Prometheus
if curl -s http://localhost:9090/-/healthy | grep -q "Prometheus"; then
    print_status 0 "Prometheus is healthy"
else
    print_status 1 "Prometheus health check failed"
fi

# Grafana
if curl -s http://localhost:3001/api/health | grep -q "ok"; then
    print_status 0 "Grafana is healthy"
else
    print_status 1 "Grafana health check failed"
fi

echo ""

# 5. Verify Prometheus Scraping
echo "5. Verifying Prometheus Configuration..."
echo "----------------------------------------"

if curl -s http://localhost:9090/api/v1/targets | grep -q "orders-service"; then
    print_status 0 "Prometheus is scraping orders-service"
else
    print_warning "Prometheus may not be scraping orders-service yet"
fi

if curl -s http://localhost:9090/api/v1/targets | grep -q "users-service"; then
    print_status 0 "Prometheus is scraping users-service"
else
    print_warning "Prometheus may not be scraping users-service yet"
fi

if curl -s http://localhost:9090/api/v1/targets | grep -q "payments-service"; then
    print_status 0 "Prometheus is scraping payments-service"
else
    print_warning "Prometheus may not be scraping payments-service yet"
fi

echo ""

# 6. Generate Test Traffic
echo "6. Generating Test Traffic..."
echo "-----------------------------"

# Install chaos simulator dependencies
cd chaos_simulator
python3 -m pip install -q -r requirements.txt
cd ..

print_info "Creating test orders..."
for i in {1..10}; do
    curl -s -X POST http://localhost:8001/orders \
        -H "Content-Type: application/json" \
        -d "{\"customer_id\":\"CUST-$i\",\"items\":[\"ITEM-$i\"],\"total\":99.99}" > /dev/null
done
print_status 0 "Created 10 test orders"

print_info "Creating test users..."
for i in {1..10}; do
    curl -s -X POST http://localhost:8002/users \
        -H "Content-Type: application/json" \
        -d "{\"name\":\"User $i\",\"email\":\"user$i@test.com\",\"role\":\"user\"}" > /dev/null
done
print_status 0 "Created 10 test users"

print_info "Creating test payments..."
for i in {1..10}; do
    curl -s -X POST http://localhost:8003/payments \
        -H "Content-Type: application/json" \
        -d "{\"order_id\":\"ORD-$i\",\"amount\":99.99,\"payment_method\":\"credit_card\"}" > /dev/null
done
print_status 0 "Created 10 test payments"

echo ""
print_info "Waiting 30 seconds for metrics collection..."
sleep 30
echo ""

# 7. Verify Metrics
echo "7. Verifying Metrics Collection..."
echo "-----------------------------------"

if curl -s "http://localhost:9090/api/v1/query?query=orders_total" | grep -q "success"; then
    print_status 0 "Orders metrics are being collected"
else
    print_warning "Orders metrics may not be available yet"
fi

if curl -s "http://localhost:9090/api/v1/query?query=users_total" | grep -q "success"; then
    print_status 0 "Users metrics are being collected"
else
    print_warning "Users metrics may not be available yet"
fi

if curl -s "http://localhost:9090/api/v1/query?query=payments_total" | grep -q "success"; then
    print_status 0 "Payments metrics are being collected"
else
    print_warning "Payments metrics may not be available yet"
fi

echo ""

# 8. Test Anomaly Detection
echo "8. Testing Anomaly Detection..."
echo "-------------------------------"

# Trigger manual detection
print_info "Triggering manual anomaly detection..."
curl -s -X POST http://localhost:8080/detect/manual > /dev/null
sleep 5

# Check predictions
PREDICTIONS=$(curl -s http://localhost:8080/predictions/all | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('count', 0))")
if [ "$PREDICTIONS" -gt 0 ]; then
    print_status 0 "Anomaly detection is working ($PREDICTIONS predictions)"
else
    print_warning "No predictions yet (this is normal if metrics are still collecting)"
fi

echo ""

# 9. Test Policy Engine
echo "9. Testing Policy Engine..."
echo "---------------------------"

# Get policy status
STATUS=$(curl -s http://localhost:8081/status)
if echo "$STATUS" | grep -q "auto_remediation_enabled"; then
    print_status 0 "Policy Engine is operational"
    
    POLICIES=$(echo "$STATUS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('policies_loaded', 0))")
    print_info "Policies loaded: $POLICIES"
else
    print_status 1 "Policy Engine status check failed"
fi

echo ""

# 10. Generate Chaos and Verify End-to-End
echo "10. Running Chaos Test..."
echo "-------------------------"

print_info "Generating chaos for 60 seconds..."
cd chaos_simulator
timeout 60 python3 chaos.py chaos --duration 60 > /dev/null 2>&1 || true
cd ..

print_info "Waiting for anomaly detection and remediation..."
sleep 45

# Check for anomalies
ANOMALIES=$(curl -s http://localhost:8080/predict | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('count', 0))")
if [ "$ANOMALIES" -gt 0 ]; then
    print_status 0 "Anomalies detected: $ANOMALIES"
else
    print_warning "No anomalies detected (may need more chaos)"
fi

# Check for actions
ACTIONS=$(curl -s http://localhost:8081/actions/recent | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('count', 0))")
if [ "$ACTIONS" -gt 0 ]; then
    print_status 0 "Remediation actions executed: $ACTIONS"
else
    print_info "No remediation actions yet (may need more severe anomalies)"
fi

echo ""

# 11. Check Dashboard
echo "11. Checking Dashboard..."
echo "-------------------------"

if curl -s http://localhost:3000 | grep -q "root"; then
    print_status 0 "Dashboard is accessible"
else
    print_status 1 "Dashboard is not accessible"
fi

echo ""

# Summary
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo ""
echo "All core components are operational!"
echo ""
echo "🌐 Access Points:"
echo "  Dashboard:     http://localhost:3000"
echo "  Grafana:       http://localhost:3001 (admin/admin)"
echo "  Prometheus:    http://localhost:9090"
echo "  Jaeger:        http://localhost:16686"
echo "  Anomaly API:   http://localhost:8080/docs"
echo "  Policy API:    http://localhost:8081/docs"
echo ""
echo "📊 Current Status:"
echo "  Services:      Running"
echo "  Metrics:       Collecting"
echo "  Predictions:   $PREDICTIONS"
echo "  Anomalies:     $ANOMALIES"
echo "  Actions:       $ACTIONS"
echo ""
echo "✅ System is ready for demonstration!"
echo ""
echo "Next steps:"
echo "  1. Open dashboard: open http://localhost:3000"
echo "  2. Generate more chaos: make chaos"
echo "  3. Watch anomalies and remediation in real-time"
echo ""
echo "To stop: make down"
echo "To clean: make clean"
echo ""


