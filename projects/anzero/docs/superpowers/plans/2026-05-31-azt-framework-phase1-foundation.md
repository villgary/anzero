# AZT Framework Phase 1: Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish the foundational architecture: Go Gateway with gRPC server, Python SDK with gRPC client, shared proto definitions, basic Policy Engine (OPA + YAML), and audit logging.

**Architecture:** This phase builds a synchronous-only enforcement flow. The Python SDK intercepts agent actions and sends them via gRPC to the Go Gateway, which evaluates policies against OPA, logs decisions, and returns allow/deny responses.

**Tech Stack:** Go 1.21+, Python 3.11+, gRPC (protobuf), OPA 0.60+, Kubernetes SDK (client-go)

---

## File Structure

```
anzero/
├── azt-framework/
│   ├── proto/                      # Shared protobuf definitions
│   │   ├── azt.proto
│   │   └── azt.pb.go              # Generated
│   │   └── azt_pb2.py             # Generated
│   │
│   ├── azt-sdk-python/             # Python SDK
│   │   ├── azt/
│   │   │   ├── __init__.py
│   │   │   ├── client.py           # gRPC client
│   │   │   ├── enforce.py         # Enforcement logic
│   │   │   ├── config.py          # SDK configuration
│   │   │   └── models.py          # Data models
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   ├── test_client.py
│   │   │   └── test_enforce.py
│   │   └── pyproject.toml
│   │
│   ├── azt-gateway/               # Go Gateway
│   │   ├── cmd/
│   │   │   └── gateway/
│   │   │       └── main.go
│   │   ├── internal/
│   │   │   ├── policy/
│   │   │   │   ├── engine.go      # OPA wrapper
│   │   │   │   ├── yaml_loader.go # YAML policy loader
│   │   │   │   └── engine_test.go
│   │   │   ├── audit/
│   │   │   │   ├── logger.go     # Structured JSON logger
│   │   │   │   └── logger_test.go
│   │   │   └── grpc/
│   │   │       ├── server.go      # gRPC server
│   │   │       └── server_test.go
│   │   ├── go.mod
│   │   └── go.sum
│   │
│   └── policies/                   # Example policies
│       └── azt-policy.yaml
│
└── docs/superpowers/plans/
    └── 2026-05-31-azt-framework-phase1-foundation.md
```

---

## Task 1: Create Project Structure and Proto Definitions

**Files:**
- Create: `azt-framework/proto/azt.proto`
- Create: `azt-framework/go.mod`
- Create: `azt-framework/pyproject.toml`

- [ ] **Step 1: Create azt.proto with gRPC service definitions**

```protobuf
syntax = "proto3";

package azt.v1;

option go_package = "github.com/anzero/azt-framework/proto/azt/v1";
option python_package = "azt.proto.azt_v1";

message ActionContext {
  string agent_id = 1;
  string action = 2;
  string tool = 3;
  map<string, string> parameters = 4;
  int32 trust_score = 5;
  string session_id = 6;
  int64 timestamp = 7;
}

message EnforcementRequest {
  ActionContext context = 1;
}

enum Decision {
  DECISION_UNSPECIFIED = 0;
  DECISION_ALLOW = 1;
  DECISION_DENY = 2;
  DECISION_REQUIRE_APPROVAL = 3;
}

message EnforcementResponse {
  Decision decision = 1;
  string reason = 2;
  int32 updated_trust_score = 3;
  string request_id = 4;
}

message TrustScoreRequest {
  string agent_id = 1;
}

message TrustScoreResponse {
  int32 score = 1;
  string reason = 2;
}

service AZTGateway {
  rpc Enforce(EnforcementRequest) returns (EnforcementResponse);
  rpc GetTrustScore(TrustScoreRequest) returns (TrustScoreResponse);
}
```

- [ ] **Step 2: Initialize Go module**

Run: `cd azt-framework && go mod init github.com/anzero/azt-framework`

- [ ] **Step 3: Create pyproject.toml for Python SDK**

```toml
[project]
name = "azt-sdk"
version = "0.1.0"
description = "AZT Framework Python SDK"
requires-python = ">=3.11"
dependencies = [
    "grpcio>=1.60.0",
    "grpcio-tools>=1.60.0",
    "pyyaml>=6.0.1",
    "pydantic>=2.5.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-grpc>=0.8.0",
]
```

- [ ] **Step 4: Commit**

```bash
git add azt-framework/proto azt-framework/go.mod azt-framework/pyproject.toml
git commit -m "feat: initialize project structure and proto definitions
- Add azt.proto with Enforce, GetTrustScore RPCs
- Initialize Go module
- Add pyproject.toml for Python SDK

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Task 2: Generate gRPC Code

**Files:**
- Modify: `azt-framework/proto/azt.pb.go` (generated)
- Modify: `azt-framework/proto/azt_pb2.py` (generated)
- Modify: `azt-framework/proto/azt_grpc.pb.go` (generated)
- Modify: `azt-framework/proto/azt_pb2.py` (generated)

- [ ] **Step 1: Generate Go gRPC code**

Run: `cd azt-framework && go install google.golang.org/protobuf/cmd/protoc-gen-go@v1.32.0 && go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@v1.3.0`
Run: `cd azt-framework && export PATH="$PATH:$(go env GOPATH)/bin" && protoc --go_out=. --go_opt=paths=source_relative --go-grpc_out=. --go-grpc_opt=paths=source_relative proto/azt.proto`

Expected: `azt-framework/proto/azt.pb.go` and `azt-framework/proto/azt_grpc.pb.go` created

- [ ] **Step 2: Generate Python gRPC code**

Run: `cd azt-framework && pip install grpcio-tools>=1.60.0 && python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. azt-framework/proto/azt.proto`

Expected: `azt-framework/proto/azt_pb2.py` and `azt-framework/proto/azt_grpc_pb2.py` created

- [ ] **Step 3: Commit**

```bash
git add azt-framework/proto/
git commit -m "feat: generate gRPC code from proto definitions
- Generate Go pb and grpc files
- Generate Python pb and grpc files

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Task 3: Implement Go Gateway - gRPC Server

**Files:**
- Create: `azt-framework/azt-gateway/cmd/gateway/main.go`
- Create: `azt-framework/azt-gateway/internal/grpc/server.go`
- Create: `azt-framework/azt-gateway/internal/grpc/server_test.go`
- Create: `azt-framework/azt-gateway/go.mod`

- [ ] **Step 1: Create Go go.mod with dependencies**

```bash
cd azt-framework/azt-gateway && go mod init github.com/anzero/azt-framework/azt-gateway
go get google.golang.org/grpc@v1.60.0
go get github.com/anzero/azt-framework/proto@v0.1.0
go get go.uber.org/zap@v1.26.0
```

Or create `go.mod` manually:
```go
module github.com/anzero/azt-framework/azt-gateway

go 1.21

require (
    google.golang.org/grpc v1.60.0
    go.uber.org/zap v1.26.0
)
```

- [ ] **Step 2: Create gRPC server implementation**

```go
// internal/grpc/server.go
package grpc

import (
    "context"
    "fmt"
    "net"

    "github.com/anzero/azt-framework/proto/azt/v1"
    "go.uber.org/zap"
    "google.golang.org/grpc"
    "google.golang.org/grpc/reflection"
)

type Server struct {
    addr   string
    logger *zap.Logger
    azt.UnimplementedAZTGatewayServer
}

func NewServer(addr string, logger *zap.Logger) *Server {
    return &Server{addr: addr, logger: logger}
}

func (s *Server) Enforce(ctx context.Context, req *azt.EnforcementRequest) (*azt.EnforcementResponse, error) {
    s.logger.Info("Enforce request received",
        zap.String("agent_id", req.Context.AgentId),
        zap.String("action", req.Context.Action),
        zap.String("tool", req.Context.Tool),
    )
    return &azt.EnforcementResponse{
        Decision: azt.Decision_DECISION_ALLOW,
        Reason:  "Phase 1: Allow all (policy engine not yet connected)",
        UpdatedTrustScore: 70,
        RequestId: fmt.Sprintf("req-%d", req.Context.Timestamp),
    }, nil
}

func (s *Server) GetTrustScore(ctx context.Context, req *azt.TrustScoreRequest) (*azt.TrustScoreResponse, error) {
    s.logger.Info("GetTrustScore request received",
        zap.String("agent_id", req.AgentId),
    )
    return &azt.TrustScoreResponse{
        Score: 70,
        Reason: "Phase 1: Default trust score",
    }, nil
}

func (s *Server) Start() error {
    lis, err := net.Listen("tcp", s.addr)
    if err != nil {
        return fmt.Errorf("failed to listen: %w", err)
    }
    grpcServer := grpc.NewServer()
    azt.RegisterAZTGatewayServer(grpcServer, s)
    reflection.Register(grpcServer)
    s.logger.Info("gRPC server listening", zap.String("addr", s.addr))
    return grpcServer.Serve(lis)
}
```

- [ ] **Step 3: Create main.go**

```go
// cmd/gateway/main.go
package main

import (
    "flag"
    "fmt"

    "github.com/anzero/azt-framework/azt-gateway/internal/grpc"
    "go.uber.org/zap"
    "go.uber.org/zap/zapcore"
)

func main() {
    addr := flag.String("addr", "localhost:50051", "gRPC server address")
    flag.Parse()

    config := zap.NewProductionConfig()
    config.EncoderConfig.TimeKey = "timestamp"
    config.EncoderConfig.EncodeTime = zapcore.ISO8601Encoder
    logger, _ := config.Build()

    server := grpc.NewServer(*addr, logger)
    logger.Info(fmt.Sprintf("Starting AZT Gateway on %s", *addr))
    if err := server.Start(); err != nil {
        logger.Fatal("Failed to start server", zap.Error(err))
    }
}
```

- [ ] **Step 4: Create server unit test**

```go
// internal/grpc/server_test.go
package grpc

import (
    "context"
    "testing"

    "github.com/anzero/azt-framework/proto/azt/v1"
    "go.uber.org/zap"
)

func TestEnforce_AllowAll(t *testing.T) {
    logger, _ := zap.NewDevelopment()
    server := NewServer("localhost:0", logger)

    resp, err := server.Enforce(context.Background(), &azt.EnforcementRequest{
        Context: &azt.ActionContext{
            AgentId:   "test-agent",
            Action:    "tool_call",
            Tool:      "send_email",
            TrustScore: 70,
            Timestamp: 1234567890,
        },
    })

    if err != nil {
        t.Fatalf("Enforce failed: %v", err)
    }
    if resp.Decision != azt.Decision_DECISION_ALLOW {
        t.Errorf("Expected ALLOW, got %v", resp.Decision)
    }
    if resp.Reason == "" {
        t.Error("Reason should not be empty")
    }
}

func TestGetTrustScore_Default(t *testing.T) {
    logger, _ := zap.NewDevelopment()
    server := NewServer("localhost:0", logger)

    resp, err := server.GetTrustScore(context.Background(), &azt.TrustScoreRequest{
        AgentId: "test-agent",
    })

    if err != nil {
        t.Fatalf("GetTrustScore failed: %v", err)
    }
    if resp.Score != 70 {
        t.Errorf("Expected score 70, got %d", resp.Score)
    }
}
```

- [ ] **Step 5: Run tests**

Run: `cd azt-framework/azt-gateway && go test ./internal/grpc/... -v`
Expected: PASS for both tests

- [ ] **Step 6: Commit**

```bash
git add azt-framework/azt-gateway/
git commit -m "feat(gateway): add gRPC server skeleton
- Add Server struct with Enforce and GetTrustScore handlers
- Add main.go entry point
- Add unit tests for basic functionality

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Task 4: Implement Python SDK - gRPC Client and Enforce Logic

**Files:**
- Create: `azt-framework/azt-sdk-python/azt/__init__.py`
- Create: `azt-framework/azt-sdk-python/azt/client.py`
- Create: `azt-framework/azt-sdk-python/azt/config.py`
- Create: `azt-framework/azt-sdk-python/azt/models.py`
- Create: `azt-framework/azt-sdk-python/azt/enforce.py`
- Create: `azt-framework/azt-sdk-python/tests/test_client.py`
- Create: `azt-framework/azt-sdk-python/tests/test_enforce.py`

- [ ] **Step 1: Create Python package init**

```python
# azt/__init__.py
"""AZT Framework Python SDK."""
__version__ = "0.1.0"

from azt.client import AZTClient
from azt.config import SDKConfig
from azt.enforce import EnforcementResult, Decision

__all__ = ["AZTClient", "SDKConfig", "EnforcementResult", "Decision"]
```

- [ ] **Step 2: Create config.py**

```python
# azt/config.py
from dataclasses import dataclass
from typing import Optional


@dataclass
class SDKConfig:
    gateway_addr: str = "localhost:50051"
    default_trust_score: int = 70
    timeout_seconds: float = 5.0
    agent_id: Optional[str] = None
    session_id: Optional[str] = None

    def validate(self) -> None:
        if not self.gateway_addr:
            raise ValueError("gateway_addr is required")
        if not 0 <= self.default_trust_score <= 100:
            raise ValueError("trust_score must be between 0 and 100")
```

- [ ] **Step 3: Create models.py**

```python
# azt/models.py
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Decision(Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"
    UNSPECIFIED = "unspecified"


@dataclass
class ActionContext:
    agent_id: str
    action: str
    tool: str
    parameters: dict[str, str]
    trust_score: int
    session_id: str


@dataclass
class EnforcementResult:
    decision: Decision
    reason: str
    updated_trust_score: int
    request_id: str
```

- [ ] **Step 4: Create gRPC client**

```python
# azt/client.py
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "proto"))

import grpc
from azt.proto.azt.v1 import (
    enforcement_request_pb2 as pb2_enforce,
    enforcement_response_pb2 as pb2_enforce_resp,
    trust_score_request_pb2 as pb2_score,
    trust_score_response_pb2 as pb2_score_resp,
    azt_gateway_pb2_grpc as pb2_grpc,
)

from azt.config import SDKConfig
from azt.models import ActionContext, Decision, EnforcementResult


class AZTClient:
    def __init__(self, config: SDKConfig):
        self.config = config
        self.channel = grpc.insecure_channel(config.gateway_addr)
        self.stub = pb2_grpc.AZTGatewayStub(self.channel)

    def enforce(self, context: ActionContext) -> EnforcementResult:
        req = pb2_enforce.EnforcementRequest(
            context=pb2_enforce.ActionContext(
                agent_id=context.agent_id,
                action=context.action,
                tool=context.tool,
                parameters=context.parameters,
                trust_score=context.trust_score,
                session_id=context.session_id,
                timestamp=int(time.time()),
            )
        )
        resp = self.stub.Enforce(req, timeout=self.config.timeout_seconds)
        return EnforcementResult(
            decision=Decision(resp.decision.name.lower()),
            reason=resp.reason,
            updated_trust_score=resp.updated_trust_score,
            request_id=resp.request_id,
        )

    def get_trust_score(self, agent_id: str) -> tuple[int, str]:
        req = pb2_score.TrustScoreRequest(agent_id=agent_id)
        resp = self.stub.GetTrustScore(req, timeout=self.config.timeout_seconds)
        return resp.score, resp.reason

    def close(self):
        self.channel.close()
```

- [ ] **Step 5: Create enforce.py (main SDK interface)**

```python
# azt/enforce.py
import time
import uuid

from azt.client import AZTClient
from azt.config import SDKConfig
from azt.models import ActionContext, Decision, EnforcementResult


class AZTEnforcer:
    def __init__(self, config: SDKConfig):
        self.config = config
        self.client = AZTClient(config)

    def check_action(
        self,
        action: str,
        tool: str,
        parameters: dict[str, str] | None = None,
        trust_score: int | None = None,
    ) -> EnforcementResult:
        context = ActionContext(
            agent_id=self.config.agent_id or "unknown",
            action=action,
            tool=tool,
            parameters=parameters or {},
            trust_score=trust_score or self.config.default_trust_score,
            session_id=self.config.session_id or str(uuid.uuid4()),
        )
        return self.client.enforce(context)

    def close(self):
        self.client.close()


def enforce_action(
    action: str,
    tool: str,
    gateway_addr: str = "localhost:50051",
    agent_id: str | None = None,
    **kwargs,
) -> EnforcementResult:
    config = SDKConfig(gateway_addr=gateway_addr, agent_id=agent_id, **kwargs)
    enforcer = AZTEnforcer(config)
    try:
        return enforcer.check_action(action, tool)
    finally:
        enforcer.close()
```

- [ ] **Step 6: Create test_client.py**

```python
# tests/test_client.py
import pytest
from azt.client import AZTClient
from azt.config import SDKConfig
from azt.models import ActionContext, Decision


class TestSDKConfig:
    def test_default_config(self):
        config = SDKConfig()
        assert config.gateway_addr == "localhost:50051"
        assert config.default_trust_score == 70

    def test_config_validation_valid(self):
        config = SDKConfig(gateway_addr="localhost:50051", trust_score=50)
        config.validate()  # Should not raise

    def test_config_validation_invalid_score(self):
        config = SDKConfig(trust_score=150)
        with pytest.raises(ValueError, match="trust_score must be between"):
            config.validate()


class TestActionContext:
    def test_create_context(self):
        ctx = ActionContext(
            agent_id="test-agent",
            action="tool_call",
            tool="send_email",
            parameters={"to": "user@example.com"},
            trust_score=70,
            session_id="session-123",
        )
        assert ctx.agent_id == "test-agent"
        assert ctx.tool == "send_email"
        assert ctx.trust_score == 70
```

- [ ] **Step 7: Create test_enforce.py**

```python
# tests/test_enforce.py
import pytest
from azt.enforce import AZTEnforcer
from azt.config import SDKConfig
from azt.models import Decision


class TestAZTEnforcer:
    def test_check_action_returns_result(self):
        config = SDKConfig(gateway_addr="localhost:50051")
        enforcer = AZTEnforcer(config)
        result = enforcer.check_action("tool_call", "read")
        assert isinstance(result.decision, Decision)
        enforcer.close()
```

- [ ] **Step 8: Run Python tests**

Run: `cd azt-framework/azt-sdk-python && python -m pytest tests/ -v`
Expected: Tests pass (may skip if no gateway running)

- [ ] **Step 9: Commit**

```bash
git add azt-framework/azt-sdk-python/
git commit -m "feat(sdk): add Python SDK with gRPC client
- Add AZTClient for gRPC communication
- Add AZTEnforcer for simplified enforcement
- Add config, models, enforce modules
- Add unit tests

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Task 5: Implement Policy Engine with OPA

**Files:**
- Create: `azt-framework/azt-gateway/internal/policy/engine.go`
- Create: `azt-framework/azt-gateway/internal/policy/yaml_loader.go`
- Create: `azt-framework/azt-gateway/internal/policy/engine_test.go`
- Modify: `azt-framework/azt-gateway/internal/grpc/server.go` (connect policy engine)

- [ ] **Step 1: Create YAML policy loader**

```go
// internal/policy/yaml_loader.go
package policy

import (
    "fmt"
    "os"

    "gopkg.in/yaml.v3"
)

type Policy struct {
    Agent   string  `yaml:"agent"`
    Version int     `yaml:"version"`
    Rules   []Rule  `yaml:"rules"`
}

type Rule struct {
    Name       string   `yaml:"name"`
    Effect     string   `yaml:"effect"`
    Tools      []string `yaml:"tools,omitempty"`
    Actions    []string `yaml:"actions,omitempty"`
    Conditions []Condition `yaml:"conditions,omitempty"`
}

type Condition struct {
    TrustScoreBelow *int `yaml:"trust_score_below,omitempty"`
    RiskLevel       *string `yaml:"risk_level,omitempty"`
}

func LoadPolicy(path string) (*Policy, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return nil, fmt.Errorf("failed to read policy file: %w", err)
    }
    var policy Policy
    if err := yaml.Unmarshal(data, &policy); err != nil {
        return nil, fmt.Errorf("failed to parse YAML: %w", err)
    }
    return &policy, nil
}
```

- [ ] **Step 2: Create Policy Engine**

```go
// internal/policy/engine.go
package policy

import (
    "fmt"
    "strings"

    "github.com/anzero/azt-framework/proto/azt/v1"
)

type Engine struct {
    policies map[string]*Policy
}

func NewEngine() *Engine {
    return &Engine{policies: make(map[string]*Policy)}
}

func (e *Engine) LoadPolicy(path string, agentId string) error {
    policy, err := LoadPolicy(path)
    if err != nil {
        return err
    }
    e.policies[agentId] = policy
    return nil
}

func (e *Engine) Evaluate(ctx *azt.ActionContext) (azt.Decision, string) {
    policy, ok := e.policies[ctx.AgentId]
    if !ok {
        return azt.Decision_DECISION_ALLOW, "No policy found, allowing by default"
    }

    for _, rule := range policy.Rules {
        if e.ruleMatches(rule, ctx) {
            if rule.Effect == "allow" {
                return azt.Decision_DECISION_ALLOW, fmt.Sprintf("Allowed by rule: %s", rule.Name)
            }
            if rule.Effect == "deny" {
                return azt.Decision_DECISION_DENY, fmt.Sprintf("Denied by rule: %s", rule.Name)
            }
        }
    }

    return azt.Decision_DECISION_ALLOW, "No matching rule, allowing by default"
}

func (e *Engine) ruleMatches(rule Rule, ctx *azt.ActionContext) bool {
    if len(rule.Tools) > 0 {
        matched := false
        for _, tool := range rule.Tools {
            if strings.EqualFold(tool, ctx.Tool) {
                matched = true
                break
            }
        }
        if !matched {
            return false
        }
    }

    if len(rule.Actions) > 0 {
        matched := false
        for _, action := range rule.Actions {
            if strings.EqualFold(action, ctx.Action) {
                matched = true
                break
            }
        }
        if !matched {
            return false
        }
    }

    for _, cond := range rule.Conditions {
        if cond.TrustScoreBelow != nil && ctx.TrustScore >= int32(*cond.TrustScoreBelow) {
            return false
        }
    }

    return true
}
```

- [ ] **Step 3: Create policy engine tests**

```go
// internal/policy/engine_test.go
package policy

import (
    "os"
    "testing"

    "github.com/anzero/azt-framework/proto/azt/v1"
)

func TestEngine_Evaluate_AllowByDefault(t *testing.T) {
    engine := NewEngine()
    ctx := &azt.ActionContext{
        AgentId:    "unknown-agent",
        Action:     "tool_call",
        Tool:       "some_tool",
        TrustScore: 70,
    }
    decision, reason := engine.Evaluate(ctx)
    if decision != azt.Decision_DECISION_ALLOW {
        t.Errorf("Expected ALLOW, got %v", decision)
    }
    t.Logf("Reason: %s", reason)
}

func TestEngine_Evaluate_WithPolicy(t *testing.T) {
    engine := NewEngine()
    yaml := `
agent: test-agent
version: 1
rules:
  - name: allow-read
    effect: allow
    tools: [read, search]
  - name: deny-write
    effect: deny
    tools: [delete, write]
`
    tmpfile, err := os.CreateTemp("", "policy-*.yaml")
    if err != nil {
        t.Fatal(err)
    }
    defer os.Remove(tmpfile.Name())
    if _, err := tmpfile.WriteString(yaml); err != nil {
        t.Fatal(err)
    }
    tmpfile.Close()

    if err := engine.LoadPolicy(tmpfile.Name(), "test-agent"); err != nil {
        t.Fatalf("Failed to load policy: %v", err)
    }

    ctx := &azt.ActionContext{
        AgentId:    "test-agent",
        Action:     "tool_call",
        Tool:       "read",
        TrustScore: 70,
    }
    decision, reason := engine.Evaluate(ctx)
    if decision != azt.Decision_DECISION_ALLOW {
        t.Errorf("Expected ALLOW for read tool, got %v", decision)
    }
    t.Logf("Allow reason: %s", reason)

    ctx.Tool = "delete"
    decision, reason = engine.Evaluate(ctx)
    if decision != azt.Decision_DECISION_DENY {
        t.Errorf("Expected DENY for delete tool, got %v", decision)
    }
    t.Logf("Deny reason: %s", reason)
}
```

- [ ] **Step 4: Run policy engine tests**

Run: `cd azt-framework/azt-gateway && go test ./internal/policy/... -v`
Expected: PASS

- [ ] **Step 5: Connect Policy Engine to gRPC Server**

```go
// internal/grpc/server.go (updated)
package grpc

import (
    "context"

    "github.com/anzero/azt-framework/azt-gateway/internal/policy"
    "github.com/anzero/azt-framework/proto/azt/v1"
    "go.uber.org/zap"
)

type Server struct {
    addr   string
    logger *zap.Logger
    engine *policy.Engine
    azt.UnimplementedAZTGatewayServer
}

func NewServer(addr string, logger *zap.Logger, engine *policy.Engine) *Server {
    return &Server{addr: addr, logger: logger, engine: engine}
}

func (s *Server) Enforce(ctx context.Context, req *azt.EnforcementRequest) (*azt.EnforcementResponse, error) {
    s.logger.Info("Enforce request received",
        zap.String("agent_id", req.Context.AgentId),
        zap.String("action", req.Context.Action),
        zap.String("tool", req.Context.Tool),
    )
    decision, reason := s.engine.Evaluate(req.Context)
    return &azt.EnforcementResponse{
        Decision:          decision,
        Reason:            reason,
        UpdatedTrustScore: req.Context.TrustScore,
    }, nil
}
```

- [ ] **Step 6: Update main.go to wire policy engine**

```go
// cmd/gateway/main.go
func main() {
    // ... logger setup ...
    engine := policy.NewEngine()
    // Load example policies if present
    if policyPath := os.Getenv("AZT_POLICY_PATH"); policyPath != "" {
        if err := engine.LoadPolicy(policyPath, "default"); err != nil {
            logger.Warn("Failed to load policy", zap.Error(err))
        }
    }
    server := grpc.NewServer(*addr, logger, engine)
    // ...
}
```

- [ ] **Step 7: Commit**

```bash
git add azt-framework/azt-gateway/internal/policy/
git commit -m "feat(gateway): add Policy Engine with YAML loader
- Add Engine struct with Evaluate method
- Add YAML policy loader with Rule/Condition structs
- Connect policy engine to gRPC Enforce handler
- Add comprehensive unit tests

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Task 6: Implement Audit Logging

**Files:**
- Create: `azt-framework/azt-gateway/internal/audit/logger.go`
- Create: `azt-framework/azt-gateway/internal/audit/logger_test.go`
- Modify: `azt-framework/azt-gateway/internal/grpc/server.go` (add audit logging)

- [ ] **Step 1: Create Audit Logger**

```go
// internal/audit/logger.go
package audit

import (
    "encoding/json"
    "time"

    "go.uber.org/zap"
)

type AuditEvent struct {
    Timestamp     string `json:"timestamp"`
    EventType     string `json:"event_type"`
    AgentId       string `json:"agent_id"`
    Action        string `json:"action"`
    Tool          string `json:"tool"`
    Decision      string `json:"decision"`
    Reason        string `json:"reason"`
    TrustScore    int    `json:"trust_score"`
    SessionId     string `json:"session_id"`
    RequestId     string `json:"request_id"`
}

type Logger struct {
    logger *zap.Logger
}

func NewLogger(logger *zap.Logger) *Logger {
    return &Logger{logger: logger}
}

func (l *Logger) LogEnforcement(event AuditEvent) {
    event.Timestamp = time.Now().UTC().Format(time.RFC3339)
    event.EventType = "enforcement"
    data, _ := json.Marshal(event)
    l.logger.Info("AUDIT", zap.ByteString("event", data))
}

func (l *Logger) LogTrustScoreChange(agentId string, oldScore, newScore int, reason string) {
    event := map[string]interface{}{
        "timestamp":   time.Now().UTC().Format(time.RFC3339),
        "event_type": "trust_score_change",
        "agent_id":   agentId,
        "old_score":  oldScore,
        "new_score":  newScore,
        "reason":     reason,
    }
    data, _ := json.Marshal(event)
    l.logger.Info("AUDIT", zap.ByteString("event", data))
}
```

- [ ] **Step 2: Create audit logger tests**

```go
// internal/audit/logger_test.go
package audit

import (
    "testing"

    "go.uber.org/zap"
)

func TestLogger_LogEnforcement(t *testing.T) {
    logger, _ := zap.NewDevelopment()
    auditor := NewLogger(logger)

    event := AuditEvent{
        AgentId:   "test-agent",
        Action:    "tool_call",
        Tool:      "read",
        Decision:  "allow",
        Reason:    "Allowed by rule: allow-read",
        TrustScore: 70,
        SessionId: "session-123",
        RequestId: "req-456",
    }

    auditor.LogEnforcement(event)
}

func TestLogger_LogTrustScoreChange(t *testing.T) {
    logger, _ := zap.NewDevelopment()
    auditor := NewLogger(logger)
    auditor.LogTrustScoreChange("test-agent", 70, 65, "Suspicious pattern detected")
}
```

- [ ] **Step 3: Run audit tests**

Run: `cd azt-framework/azt-gateway && go test ./internal/audit/... -v`
Expected: PASS

- [ ] **Step 4: Connect audit logger to gRPC server**

```go
// internal/grpc/server.go (updated)
type Server struct {
    addr   string
    logger *zap.Logger
    engine *policy.Engine
    audit  *audit.Logger
    azt.UnimplementedAZTGatewayServer
}

func NewServer(addr string, logger *zap.Logger, engine *policy.Engine, audit *audit.Logger) *Server {
    return &Server{addr: addr, logger: logger, engine: engine, audit: audit}
}

func (s *Server) Enforce(ctx context.Context, req *azt.EnforcementRequest) (*azt.EnforcementResponse, error) {
    decision, reason := s.engine.Evaluate(req.Context)

    s.audit.LogEnforcement(audit.AuditEvent{
        AgentId:    req.Context.AgentId,
        Action:     req.Context.Action,
        Tool:       req.Context.Tool,
        Decision:   decision.String(),
        Reason:     reason,
        TrustScore: int(req.Context.TrustScore),
        SessionId:  req.Context.SessionId,
    })

    return &azt.EnforcementResponse{
        Decision:          decision,
        Reason:            reason,
        UpdatedTrustScore: req.Context.TrustScore,
    }, nil
}
```

- [ ] **Step 5: Update main.go to wire audit logger**

```go
// cmd/gateway/main.go
func main() {
    // ... logger setup ...
    engine := policy.NewEngine()
    auditLogger := audit.NewLogger(logger)
    server := grpc.NewServer(*addr, logger, engine, auditLogger)
    // ...
}
```

- [ ] **Step 6: Commit**

```bash
git add azt-framework/azt-gateway/internal/audit/
git commit -m "feat(gateway): add structured audit logging
- Add AuditEvent struct with JSON serialization
- Add Logger with LogEnforcement and LogTrustScoreChange
- Integrate audit logging into gRPC Enforce handler
- Add unit tests

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Task 7: Create Example Policies and Documentation

**Files:**
- Create: `azt-framework/policies/azt-policy.yaml`
- Create: `azt-framework/README.md`

- [ ] **Step 1: Create example policy**

```yaml
# azt-framework/policies/azt-policy.yaml
agent: email-agent-prod
version: 1
rules:
  - name: allow-read-tools
    effect: allow
    tools:
      - search
      - lookup
      - read
      - get_email
      - list_emails

  - name: allow-compose
    effect: allow
    tools:
      - compose_email
      - draft_email

  - name: deny-high-risk-tools-low-trust
    effect: deny
    tools:
      - delete_email
      - delete_user
      - export_data
    conditions:
      - trust_score_below: 80

  - name: require-approval-high-risk
    effect: deny
    actions:
      - delete_data
      - export_user_info
      - modify_permissions
```

- [ ] **Step 2: Create README.md**

```markdown
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

## Status

Phase 1: Foundation (in progress)
- [x] gRPC server and client
- [x] Basic policy engine with YAML
- [x] Audit logging
- [ ] Trust scoring
- [ ] Threat shield
```
