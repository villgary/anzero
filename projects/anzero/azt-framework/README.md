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

## Status

Phase 1: Foundation (in progress)
- [x] gRPC server and client
- [x] Basic policy engine with YAML
- [x] Audit logging
- [ ] Trust scoring
- [ ] Threat shield
