# Phase 3: Threat Shield Specification

## Overview

Threat Shield is the third pillar of the AZT Framework, providing comprehensive threat detection for AI agents. It uses a parallel evaluation architecture where multiple specialized analyzers inspect each input concurrently, then a severity aggregator produces a combined threat score.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Go Gateway                                  │
│                                                                  │
│  ┌─────────────┐     ┌──────────────────────────────────────┐   │
│  │   Policy   │────►│           Threat Shield               │   │
│  │   Engine   │     │                                       │   │
│  └─────────────┘     │  ┌──────────┐ ┌──────────┐ ┌──────┐ │   │
│                      │  │  Prompt  │ │  Data    │ │Model │ │   │
│                      │  │Injection │ │Exfiltrat.│ │ Abuse│ │   │
│                      │  └────┬─────┘ └────┬─────┘ └──┬───┘ │   │
│                      │       │             │          │     │   │
│                      │  ┌────▼─────────────▼──────────▼────┐ │   │
│                      │  │     Severity Aggregator          │ │   │
│                      │  └──────────────────────────────────┘ │   │
│                      └──────────────────────────────────────┘   │
│                              │                                    │
│                      ┌───────▼───────┐                           │
│                      │  PostgreSQL   │ (custom patterns, history) │
│                      └───────────────┘                           │
└─────────────────────────────────────────────────────────────────┘
```

## Evaluation Chain

1. **Policy Engine** evaluates first (trust score + rules)
   - If DENY → return immediately
   - If ALLOW → continue to Threat Shield

2. **Threat Shield** parallel analyzers run:
   - Prompt Injection Analyzer
   - Data Exfiltration Analyzer
   - Model Abuse Analyzer
   - Tool Abuse Analyzer

3. **Severity Aggregator** combines scores:
   - Score ≥ 80: BLOCK + alert
   - Score 50-79: LOG + alert
   - Score < 50: ALLOW

4. Decision returned to SDK

## Built-in Threat Feed

Patterns stored in YAML, version-controlled via GitOps.

**Location**: `azt-framework/azt-gateway/internal/shield/patterns/builtin.yaml`

```yaml
prompt_injection:
  - name: instruction_override
    patterns:
      - "(?i)ignore.{0,20}(previous|all|your).{0,20}(instruction|command|rule)"
      - "(?i)forget.{0,20}(everything|all|previous|you were)"
      - "(?i)you are now (a |the )"
      - "(?i)new instructions?:"
      - "(?i)system prompt:?\\s*"
      - "(?i)<\|im_start\|>.*<\|im_end\|>"
      - "(?i)\\[INST\\].*\\[/INST\\]"
    severity: critical

  - name: role_playing_jailbreak
    patterns:
      - "(?i)pretend you are (not? )?a"
      - "(?i)roleplay as (a |an )"
      - "(?i)you can (now )?ignore"
      - "(?i) DAN, .* do anything"
    severity: high

  - name: context_escape
    patterns:
      - "(?i)\\{.*\\}.*\\{.*\\}"
      - "(?i)```json\\s*\\{"
      - "(?i)<script.*>.*</script>"
      - "(?i)\\[TOOL_CALL\\]"
    severity: medium

data_exfiltration:
  - name: credential_patterns
    patterns:
      - "(?i)(api[_-]?key|token|secret|password|passwd|pwd).*['\\\"]?[a-zA-Z0-9]{16,}['\\\"]?"
      - "(?i)Bearer\\s+[a-zA-Z0-9\\-_]+\\.[a-zA-Z0-9\\-_]+\\.[a-zA-Z0-9\\-_]+"
      - "(?i)sk-[a-zA-Z0-9]{48,}"
      - "(?i)ghp_[a-zA-Z0-9]{36,}"
    severity: critical

  - name: pii_patterns
    patterns:
      - "\\b\\d{3}-\\d{2}-\\d{4}\\b"  # SSN
      - "\\b\\d{16}\\b"               # Credit card
      - "(?i)\\b(email|phone|address)\\b.*\\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}\\b"
    severity: high

model_abuse:
  - name: rapid_requests
    threshold:
      requests_per_minute: 60
      requests_per_hour: 1000
    severity: medium

  - name: token_amplification
    patterns:
      - "(?i)(repeat|loop|again).{0,20}(this|that|again)"
      - "(?i){[^{}]{200,}}"  # Large repeating structures
    severity: medium

tool_abuse:
  - name: suspicious_combinations
    sequences:
      - [read_file, delete_file, send_email]
      - [get_database, export_data, post_message]
    severity: high
```

## Optional MISP/STIX/TAXII Integration

Enterprise customers can connect to external threat intelligence.

**Feed Connector**: `azt-framework/azt-gateway/internal/shield/feed.go`

```go
type FeedConnector interface {
    FetchIOCs() ([]IOC, error)
    StartPeriodicSync(interval time.Duration)
}

type MISPConnector struct {
    URL      string
    APIKey   string
    LastSync time.Time
}
```

**IOC Structure**:
```go
type IOC struct {
    Type    string    // "prompt_injection", "exfiltration", "malicious_domain"
    Pattern string    // regex or keyword
    Severity int      // 0-100
    Source  string    // "misp", "stix", "custom"
    TTL     time.Duration
}
```

## Anomaly Detection

### Static Baseline
Policy-defined acceptable patterns:

```yaml
baseline:
  tool_sequence_max_length: 10
  requests_per_minute_max: 60
  response_size_max_kb: 4096
  unusual_hours: [0, 1, 2, 3, 4]  # UTC
```

### Adaptive Learning (Optional)
When enabled, learns from historical actions:

```go
type AdaptiveBaseline struct {
    store        *Store
    windowSize   time.Duration  // e.g., 7 days
    confidence   float64        // minimum confidence threshold
}
```

Stores behavioral baselines per agent:
- Normal tool sequences
- Typical request times
- Average response sizes
- Common tool combinations

## Database Schema

```sql
CREATE TABLE threat_patterns (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    pattern TEXT NOT NULL,
    pattern_type VARCHAR(20) NOT NULL,  -- 'regex', 'keyword', 'sequence'
    severity INTEGER NOT NULL CHECK (severity >= 0 AND severity <= 100),
    source VARCHAR(50) NOT NULL DEFAULT 'builtin',  -- 'builtin', 'custom', 'misp', 'stix'
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE threat_detections (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(255) NOT NULL,
    analyzer VARCHAR(50) NOT NULL,
    pattern_matched VARCHAR(100),
    severity INTEGER NOT NULL,
    indicators JSONB,
    context JSONB,
    action_taken VARCHAR(20) NOT NULL,  -- 'block', 'log_alert', 'allow'
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_threat_detections_agent_id ON threat_detections(agent_id);
CREATE INDEX idx_threat_detections_created_at ON threat_detections(created_at);
CREATE INDEX idx_threat_patterns_category ON threat_patterns(category);
```

## Components

### `azt-gateway/internal/shield/analyzer.go`
```go
type Analyzer interface {
    Analyze(ctx context.Context, input *ShieldInput) (*AnalyzerResult, error)
    Name() string
}

type AnalyzerResult struct {
    Analyzer   string   `json:"analyzer"`
    Score      int      `json:"score"`       // 0-100
    Indicators []string `json:"indicators"`
    MatchedRule string  `json:"matched_rule,omitempty"`
}

type ShieldInput struct {
    AgentID       string
    Action        string
    Tool          string
    Prompt        string                 `json:"prompt,omitempty"`
    Output        string                 `json:"output,omitempty"`
    Parameters    map[string]interface{} `json:"parameters,omitempty"`
    TrustScore    int                    `json:"trust_score"`
    Timestamp     int64                  `json:"timestamp"`
}
```

### `azt-gateway/internal/shield/injector.go`
Prompt injection detection using pattern matching + structural analysis.

### `azt-gateway/internal/shield/exfiltration.go`
Data exfiltration detection for credentials, PII, sensitive data.

### `azt-gateway/internal/shield/abuse.go`
Model abuse (rapid requests, token amplification) and tool abuse detection.

### `azt-gateway/internal/shield/aggregator.go`
```go
type Aggregator struct {
    weights map[string]float64  // analyzer name -> weight
    blockThreshold int           // ≥80
    alertThreshold int           // ≥50
}

func (a *Aggregator) Aggregate(results []*AnalyzerResult) (int, string) {
    // Weighted average of scores
    // Returns final score and action: BLOCK | LOG_ALERT | ALLOW
}
```

### `azt-gateway/internal/shield/baseline.go`
Static baseline validation + optional adaptive learning.

### `azt-gateway/internal/shield/feed.go`
MISP/STIX/TAXII connector for external threat intelligence.

### `azt-gateway/internal/shield/shield.go`
Main Shield struct:
```go
type Shield struct {
    analyzers  []Analyzer
    aggregator *Aggregator
    baseline  *Baseline
    feed      *FeedConnector
    store     *Store
    logger    *zap.Logger
}

func (s *Shield) Evaluate(ctx context.Context, input *ShieldInput) (*ShieldDecision, error)
```

## gRPC Integration

**Proto update** (`proto/azt.proto`):
```protobuf
message ThreatShieldRequest {
  string agent_id = 1;
  string action = 2;
  string tool = 3;
  string prompt = 4;
  string output = 5;
  map<string, string> parameters = 6;
  int32 trust_score = 7;
  int64 timestamp = 8;
}

message ThreatShieldResponse {
  string decision = 1;  // BLOCK | LOG_ALERT | ALLOW
  int32 severity_score = 2;
  repeated string indicators = 3;
  string reason = 4;
}

message AnalyzerResult {
  string analyzer = 1;
  int32 score = 2;
  repeated string indicators = 3;
  string matched_rule = 4;
}

service AZTGateway {
  rpc ThreatShieldScan(ThreatShieldRequest) returns (ThreatShieldResponse);
}
```

## Python SDK Integration

**SDK pre-filter** (`azt-sdk-python/azt/shield.py`):
```python
class ThreatShield:
    def __init__(self, gateway_addr: str):
        self.stub = azt_pb2_grpc.AZTGatewayStub(self.channel)

    def pre_filter(self, prompt: str) -> PreFilterResult:
        # Lightweight pattern check (<5ms)
        # Returns (should_block, suspicious_patterns)
        # If suspicious, send to gateway for deep scan
```

## Decision Thresholds

| Score | Action | Description |
|-------|--------|-------------|
| ≥ 80 | BLOCK | Critical threat detected, block immediately |
| 50-79 | LOG_ALERT | Suspicious activity, allow but alert |
| < 50 | ALLOW | Normal activity, log for monitoring |

## Testing Strategy

```bash
# Unit tests per analyzer
go test ./internal/shield/... -run TestInjector
go test ./internal/shield/... -run TestExfiltration
go test ./internal/shield/... -run TestAbuse

# Integration tests
go test ./internal/shield/... -run TestShield_E2E

# Pattern validation
go test ./internal/shield/... -run TestBuiltinPatterns
```

## Files to Create

```
azt-framework/azt-gateway/internal/shield/
├── shield.go              # Main Shield struct
├── analyzer.go            # Analyzer interface + registry
├── injector.go            # Prompt injection detection
├── exfiltration.go        # Data exfiltration detection
├── abuse.go               # Model/tool abuse detection
├── aggregator.go          # Severity scoring + threshold
├── baseline.go            # Static + adaptive baseline
├── feed.go                # MISP/STIX connector
├── patterns/
│   └── builtin.go         # Built-in threat patterns
└── shield_test.go

azt-framework/migrations/002_create_shield_tables.sql

azt-framework/azt-sdk-python/azt/shield.py

azt-framework/proto/azt.proto  (add ThreatShieldScan RPC)
```

## Implementation Phases

### Phase 3.1: Core Shield
- Shield struct with aggregator
- Built-in patterns (YAML loader)
- Prompt injection analyzer
- Basic gRPC integration

### Phase 3.2: Additional Analyzers
- Data exfiltration analyzer
- Model abuse analyzer
- Tool abuse analyzer
- PostgreSQL pattern store

### Phase 3.3: Advanced Features
- Adaptive baseline learning
- MISP/STIX connector
- SDK pre-filter integration
- End-to-end tests
