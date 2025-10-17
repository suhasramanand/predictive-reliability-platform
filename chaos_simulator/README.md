# Chaos Simulator

Tool for injecting failures and stress into microservices.

## Usage

```bash
# Check service health
python chaos.py health

# Generate load on a specific service
python chaos.py load --service orders --requests 100

# Generate traffic spike
python chaos.py spike --service payments --duration 30

# Random chaos events
python chaos.py chaos --duration 120

# Steady background load
python chaos.py steady --duration 300
```

## Modes

- **health**: Check health of all services
- **load**: Generate specific number of requests to a service
- **spike**: Generate traffic spike for duration
- **chaos**: Random chaos events across all services
- **steady**: Steady background load on all services


