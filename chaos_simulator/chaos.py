#!/usr/bin/env python3
"""
Chaos Simulator
Injects random failures and stress into microservices
"""
import os
import sys
import time
import random
import logging
import requests
import argparse
from typing import List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Service endpoints
SERVICES = {
    "orders": "http://localhost:8001",
    "users": "http://localhost:8002",
    "payments": "http://localhost:8003",
}

class ChaosSimulator:
    """Simulates various failure scenarios"""
    
    def __init__(self, services: dict):
        self.services = services
    
    def generate_load(self, service_name: str, requests_count: int = 50):
        """Generate traffic to a service"""
        if service_name not in self.services:
            logger.error(f"Unknown service: {service_name}")
            return
        
        base_url = self.services[service_name]
        logger.info(f"Generating {requests_count} requests to {service_name}")
        
        success_count = 0
        error_count = 0
        
        for i in range(requests_count):
            try:
                if service_name == "orders":
                    response = requests.post(
                        f"{base_url}/orders",
                        json={
                            "customer_id": f"CUST-{random.randint(1000, 9999)}",
                            "items": [f"ITEM-{random.randint(1, 100)}"],
                            "total": round(random.uniform(10, 500), 2)
                        },
                        timeout=5
                    )
                elif service_name == "users":
                    response = requests.post(
                        f"{base_url}/users",
                        json={
                            "name": f"User {random.randint(1000, 9999)}",
                            "email": f"user{random.randint(1000, 9999)}@example.com",
                            "role": random.choice(["user", "admin"])
                        },
                        timeout=5
                    )
                elif service_name == "payments":
                    response = requests.post(
                        f"{base_url}/payments",
                        json={
                            "order_id": f"ORD-{random.randint(1000, 9999)}",
                            "amount": round(random.uniform(10, 500), 2),
                            "payment_method": random.choice(["credit_card", "paypal", "bank_transfer"])
                        },
                        timeout=5
                    )
                
                if response.status_code < 400:
                    success_count += 1
                else:
                    error_count += 1
                
            except Exception as e:
                error_count += 1
                logger.debug(f"Request failed: {e}")
            
            time.sleep(random.uniform(0.05, 0.2))
        
        logger.info(
            f"Load generation complete: {success_count} success, "
            f"{error_count} errors"
        )
    
    def spike_traffic(self, service_name: str, duration: int = 30):
        """Generate traffic spike"""
        logger.info(f"Generating traffic spike on {service_name} for {duration}s")
        
        start_time = time.time()
        request_count = 0
        
        while time.time() - start_time < duration:
            try:
                self.generate_load(service_name, requests_count=10)
                request_count += 10
            except KeyboardInterrupt:
                break
        
        logger.info(f"Traffic spike complete: {request_count} total requests")
    
    def random_chaos(self, duration: int = 60):
        """Inject random chaos into random services"""
        logger.info(f"Starting random chaos for {duration}s")
        
        start_time = time.time()
        chaos_events = 0
        
        while time.time() - start_time < duration:
            try:
                # Pick random service
                service = random.choice(list(self.services.keys()))
                
                # Pick random chaos type
                chaos_type = random.choice([
                    "load",
                    "burst",
                    "rapid_requests"
                ])
                
                if chaos_type == "load":
                    logger.info(f"[CHAOS] Generating load on {service}")
                    self.generate_load(service, requests_count=random.randint(20, 50))
                elif chaos_type == "burst":
                    logger.info(f"[CHAOS] Generating burst on {service}")
                    self.generate_load(service, requests_count=random.randint(50, 100))
                elif chaos_type == "rapid_requests":
                    logger.info(f"[CHAOS] Rapid requests to {service}")
                    for _ in range(random.randint(10, 30)):
                        self.generate_load(service, requests_count=1)
                        time.sleep(0.1)
                
                chaos_events += 1
                
                # Wait before next chaos event
                time.sleep(random.uniform(5, 15))
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Chaos event failed: {e}")
        
        logger.info(f"Random chaos complete: {chaos_events} events executed")
    
    def steady_load(self, duration: int = 300):
        """Generate steady background load"""
        logger.info(f"Starting steady load for {duration}s")
        
        start_time = time.time()
        request_count = 0
        
        while time.time() - start_time < duration:
            try:
                # Rotate through services
                for service in self.services.keys():
                    self.generate_load(service, requests_count=5)
                    request_count += 5
                    time.sleep(2)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Error in steady load: {e}")
        
        logger.info(f"Steady load complete: {request_count} total requests")
    
    def health_check_all(self):
        """Check health of all services"""
        logger.info("Checking health of all services")
        
        for service_name, base_url in self.services.items():
            try:
                response = requests.get(f"{base_url}/health", timeout=5)
                if response.status_code == 200:
                    logger.info(f"✓ {service_name}: healthy")
                else:
                    logger.warning(f"✗ {service_name}: unhealthy (status {response.status_code})")
            except Exception as e:
                logger.error(f"✗ {service_name}: unreachable ({e})")

def main():
    parser = argparse.ArgumentParser(description="Chaos Simulator for Microservices")
    parser.add_argument(
        "mode",
        choices=["load", "spike", "chaos", "steady", "health"],
        help="Chaos mode to run"
    )
    parser.add_argument(
        "--service",
        choices=list(SERVICES.keys()),
        help="Target service (for load/spike modes)"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=60,
        help="Duration in seconds (default: 60)"
    )
    parser.add_argument(
        "--requests",
        type=int,
        default=50,
        help="Number of requests (for load mode, default: 50)"
    )
    
    args = parser.parse_args()
    
    simulator = ChaosSimulator(SERVICES)
    
    try:
        if args.mode == "health":
            simulator.health_check_all()
        
        elif args.mode == "load":
            if not args.service:
                logger.error("--service is required for load mode")
                sys.exit(1)
            simulator.generate_load(args.service, args.requests)
        
        elif args.mode == "spike":
            if not args.service:
                logger.error("--service is required for spike mode")
                sys.exit(1)
            simulator.spike_traffic(args.service, args.duration)
        
        elif args.mode == "chaos":
            simulator.random_chaos(args.duration)
        
        elif args.mode == "steady":
            simulator.steady_load(args.duration)
    
    except KeyboardInterrupt:
        logger.info("\nChaos simulation interrupted by user")
    except Exception as e:
        logger.error(f"Chaos simulation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


