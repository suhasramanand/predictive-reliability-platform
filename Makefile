.PHONY: help up down build logs status chaos health clean test

# Default target
help:
	@echo "Predictive Reliability Platform - Makefile Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make up          - Start all services"
	@echo "  make down        - Stop all services"
	@echo "  make build       - Build all Docker images"
	@echo "  make rebuild     - Rebuild and restart all services"
	@echo "  make logs        - View logs from all services"
	@echo "  make status      - Check status of all services"
	@echo "  make health      - Check health of microservices"
	@echo "  make chaos       - Inject random chaos"
	@echo "  make chaos-load  - Generate steady load"
	@echo "  make chaos-spike - Generate traffic spike"
	@echo "  make clean       - Stop services and remove volumes"
	@echo "  make test        - Run end-to-end test"
	@echo "  make urls        - Display service URLs"

# Start all services
up:
	@echo "🚀 Starting Predictive Reliability Platform..."
	docker-compose up -d
	@echo ""
	@echo "✅ Services started successfully!"
	@echo ""
	@$(MAKE) urls

# Stop all services
down:
	@echo "🛑 Stopping all services..."
	docker-compose down
	@echo "✅ All services stopped"

# Build all images
build:
	@echo "🔨 Building Docker images..."
	docker-compose build

# Rebuild and restart
rebuild:
	@echo "🔄 Rebuilding and restarting..."
	docker-compose down
	docker-compose build
	docker-compose up -d
	@echo "✅ Services rebuilt and restarted"

# View logs
logs:
	docker-compose logs -f

# Check service status
status:
	@echo "📊 Service Status:"
	@docker-compose ps

# Health check
health:
	@echo "🏥 Checking service health..."
	@echo ""
	@echo "Orders Service:"
	@curl -s http://localhost:8001/health | python3 -m json.tool || echo "❌ Not responding"
	@echo ""
	@echo "Users Service:"
	@curl -s http://localhost:8002/health | python3 -m json.tool || echo "❌ Not responding"
	@echo ""
	@echo "Payments Service:"
	@curl -s http://localhost:8003/health | python3 -m json.tool || echo "❌ Not responding"
	@echo ""
	@echo "Anomaly Service:"
	@curl -s http://localhost:8080/health | python3 -m json.tool || echo "❌ Not responding"
	@echo ""
	@echo "Policy Engine:"
	@curl -s http://localhost:8081/health | python3 -m json.tool || echo "❌ Not responding"

# Inject chaos
chaos:
	@echo "💥 Injecting random chaos for 120 seconds..."
	cd chaos_simulator && python3 -m pip install -q -r requirements.txt
	cd chaos_simulator && python3 chaos.py chaos --duration 120

# Generate steady load
chaos-load:
	@echo "📈 Generating steady load for 300 seconds..."
	cd chaos_simulator && python3 -m pip install -q -r requirements.txt
	cd chaos_simulator && python3 chaos.py steady --duration 300

# Generate traffic spike
chaos-spike:
	@echo "⚡ Generating traffic spike on orders service..."
	cd chaos_simulator && python3 -m pip install -q -r requirements.txt
	cd chaos_simulator && python3 chaos.py spike --service orders --duration 60

# Clean everything
clean:
	@echo "🧹 Cleaning up..."
	docker-compose down -v
	@echo "✅ Cleanup complete"

# Run end-to-end test
test:
	@echo "🧪 Running end-to-end test..."
	@echo ""
	@echo "1. Checking service health..."
	@$(MAKE) health
	@echo ""
	@echo "2. Generating test traffic..."
	cd chaos_simulator && python3 -m pip install -q -r requirements.txt
	cd chaos_simulator && python3 chaos.py load --service orders --requests 20
	@echo ""
	@echo "3. Checking for anomalies..."
	@sleep 5
	@curl -s http://localhost:8080/predict | python3 -m json.tool
	@echo ""
	@echo "4. Checking policy engine status..."
	@curl -s http://localhost:8081/status | python3 -m json.tool
	@echo ""
	@echo "✅ End-to-end test complete"

# Display URLs
urls:
	@echo "🌐 Service URLs:"
	@echo "  Dashboard:          http://localhost:3000"
	@echo "  Grafana:            http://localhost:3001 (admin/admin)"
	@echo "  Prometheus:         http://localhost:9090"
	@echo "  Jaeger:             http://localhost:16686"
	@echo "  Anomaly API:        http://localhost:8080/docs"
	@echo "  Policy Engine API:  http://localhost:8081/docs"
	@echo ""
	@echo "  Orders Service:     http://localhost:8001/docs"
	@echo "  Users Service:      http://localhost:8002/docs"
	@echo "  Payments Service:   http://localhost:8003/docs"


