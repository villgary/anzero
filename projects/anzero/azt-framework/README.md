# AZT Framework

Zero Trust Security for AI Agents.

## Quick Start

### Start the Gateway

```bash
cd azt-gateway
go build -o gateway ./cmd/gateway
AZT_POLICY_PATH=../policies/azt-policy.yaml ./gateway --addr :50051
```

### Use the Python SDK

```python
from azt import AZTEnforcer, SDKConfig

config = SDKConfig(
    gateway_addr="localhost:50051",
    agent_id="my-agent"
)
enforcer = AZTEnforcer(config)
result = enforcer.check_action("tool_call", "read")
print(f"Decision: {result.decision}, Reason: {result.reason}")
enforcer.close()
```

## Architecture

- **Python SDK**: Embedded in AI agent runtime
- **Go Gateway**: Centralized policy engine with OPA
- **gRPC**: Communication between SDK and gateway

## Project Structure

```
azt-framework/
├── proto/              # Protobuf definitions
├── azt-sdk-python/     # Python SDK
├── azt-gateway/        # Go Gateway
└── policies/           # Example policies
```

## Trust Scoring

Phase 2 adds dynamic trust scoring with five factors:

| Factor | Weight | Description |
|--------|--------|-------------|
| Identity | 20% | SPIFFE workload identity verification |
| Historical | 25% | Past behavior patterns |
| Time-of-Day | 15% | Business hours analysis |
| Anomaly | 20% | Contextual deviation detection |
| Frequency | 20% | Tool usage patterns |

### Database Setup

The gateway requires PostgreSQL. Set the connection URL:

```bash
export DB_URL="postgres://user:pass@localhost:5432/azt?sslmode=disable"
./gateway --db-url=$DB_URL
```

### Using Trust Scoring

```python
from azt import AZTClient, SDKConfig

client = AZTClient(SDKConfig(gateway_addr="localhost:50051"))

# Get current trust score
result = client.get_agent_score("my-agent")
print(f"Score: {result['score']}")
print(f"Breakdown: {result['breakdown']}")

# Update trust score with action context
result = client.update_trust_score(
    agent_id="my-agent",
    factor="history",
    delta=-10,
    reason="Policy denial",
    action_context={"tool": "delete", "action": "tool_call"}
)
print(f"New score: {result['score']}")
```

## Status

Phase 1: Foundation (in progress)
- [x] gRPC server and client
- [x] Basic policy engine with YAML
- [x] Audit logging
- [ ] Trust scoring
- [ ] Threat shield
