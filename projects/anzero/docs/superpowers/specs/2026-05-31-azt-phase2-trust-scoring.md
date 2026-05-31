# Phase 2: Trust Scoring Service Specification

## Overview

Phase 2 implements the Trust Scoring pillar of the AZT Framework. Each AI agent receives a dynamic trust score (0–100) based on five factors. The score influences Policy Engine decisions and communication patterns.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Go Gateway                               │
│  ┌─────────────────┐  ┌──────────────────┐                │
│  │  Trust Scoring  │  │   Policy Engine  │                │
│  │    Service      │◄─┤                  │                │
│  └────────┬────────┘  └──────────────────┘                │
│           │                                                  │
│  ┌────────▼────────┐                                       │
│  │  PostgreSQL     │  (persistent score storage)           │
│  └─────────────────┘                                       │
└─────────────────────────────────────────────────────────────┘
```

## Scoring Factors

| Factor | Weight | Description |
|--------|--------|-------------|
| Identity (SPIFFE) | 20% | Verifies agent workload identity via SPIFFE SVID |
| Historical behavior | 25% | Based on past action patterns and policy decisions |
| Time-of-day | 15% | Unusual hours = lower score |
| Contextual anomalies | 20% | Deviation from normal context (tool, parameters, session) |
| Tool usage frequency | 20% | Unusual tool access frequency patterns |

**Score Range**: 0–100 (default starts at 70)

**Score Thresholds**:
- 80–100: Full sync enforcement
- 60–79: Sync for high-risk, async for low-risk
- Below 60: All actions require approval or denied

## Database Schema

```sql
CREATE TABLE agent_scores (
    agent_id VARCHAR(255) PRIMARY KEY,
    score INTEGER NOT NULL DEFAULT 70 CHECK (score >= 0 AND score <= 100),
    identity_verified BOOLEAN DEFAULT FALSE,
    last_action_at TIMESTAMP,
    last_updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE score_history (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(255) NOT NULL REFERENCES agent_scores(agent_id),
    previous_score INTEGER NOT NULL,
    new_score INTEGER NOT NULL,
    delta INTEGER NOT NULL,
    factor VARCHAR(50) NOT NULL,
    reason TEXT,
    action_context JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_score_history_agent_id ON score_history(agent_id);
CREATE INDEX idx_score_history_created_at ON score_history(created_at);
```

## Components

### 1. Trust Scoring Service (`internal/trust/`)

**scorer.go**
- `Scorer` struct with all five factor calculators
- `CalculateScore(ctx, agentId, actionContext) (int, FactorBreakdown)`
- Each factor: `evaluateIdentity()`, `evaluateHistory()`, `evaluateTimeOfDay()`, `evaluateAnomalies()`, `evaluateToolFrequency()`

**store.go**
- PostgreSQL storage layer
- `GetScore(agentId) (AgentScore, error)`
- `UpdateScore(agentId, newScore, delta, factor, reason) error`
- `GetHistory(agentId, limit) ([]ScoreHistory, error)`
- `InitSchema() error` - creates tables if not exist

**analyzer.go**
- Anomaly detection for contextual analysis
- `DetectContextAnomalies(ctx, currentContext, historicalContexts) (anomalyScore, bool)`
- Uses simple statistical deviation detection

### 2. Factor Evaluation

**Identity Factor (20%)**
```
- SPIFFE SVID verified: +10
- SPIFFE SVID invalid/missing: -20
- First time agent seen: neutral (0)
```

**Historical Factor (25%)**
```
- Consistent behavior (past 100 actions similar): +5
- Policy DENY ratio > 20%: -15
- Policy DENY ratio > 50%: -25
- No history yet: neutral (0)
```

**Time-of-Day Factor (15%)**
```
- Access during configured hours: +5
- Access outside configured hours: -10
- First access at unusual hour: -5
```

**Anomaly Factor (20%)**
```
- Context within normal variance: +5
- Deviation from historical context: -10 to -20
- New tool/parameter combination: -15
```

**Tool Frequency Factor (20%)**
```
- Normal tool usage patterns: +5
- Sudden spike in tool calls (>3x average): -15
- Accessing unusual tools: -10
```

### 3. gRPC Integration

**Proto Updates** (`proto/azt.proto`):
```protobuf
message UpdateScoreRequest {
  string agent_id = 1;
  string factor = 2;
  int32 delta = 3;
  string reason = 4;
}

message ScoreResponse {
  int32 score = 1;
  string reason = 2;
  FactorBreakdown breakdown = 3;
}

message FactorBreakdown {
  int32 identity_score = 1;
  int32 history_score = 2;
  int32 time_score = 3;
  int32 anomaly_score = 4;
  int32 frequency_score = 5;
}

service AZTGateway {
  // ... existing methods ...
  rpc UpdateTrustScore(UpdateScoreRequest) returns (ScoreResponse);
  rpc GetAgentScore(TrustScoreRequest) returns (ScoreResponse);
}
```

### 4. Policy Engine Integration

The Policy Engine (Phase 1) already receives `trust_score` in `ActionContext`. Trust Scoring now:
1. Provides actual scores instead of default 70
2. Updates scores based on action outcomes
3. Provides factor breakdown for detailed policy rules

### 5. Async Communication Path

**When Trust Score >= 60:**
- Low-risk actions: async enforcement with eventual consistency
- High-risk actions: sync enforcement

**When Trust Score < 60:**
- All actions: sync enforcement or require approval

## Data Flow

```
1. Agent calls tool
         │
         ▼
2. SDK sends action context to Gateway (sync or async)
         │
         ▼
3. Trust Scoring Service:
   a) Get current score from PostgreSQL
   b) Evaluate all 5 factors
   c) Calculate new score
   d) Persist to PostgreSQL
   e) Log to score_history
         │
         ▼
4. Policy Engine receives updated trust_score
         │
         ▼
5. Decision returned to SDK with score update
```

## Files to Create/Modify

### New Files
- `azt-framework/azt-gateway/internal/trust/scorer.go`
- `azt-framework/azt-gateway/internal/trust/store.go`
- `azt-framework/azt-gateway/internal/trust/analyzer.go`
- `azt-framework/azt-gateway/internal/trust/scorer_test.go`
- `azt-framework/azt-gateway/internal/trust/store_test.go`
- `azt-framework/azt-gateway/internal/trust/analyzer_test.go`
- `migrations/001_create_trust_tables.sql`

### Modified Files
- `azt-framework/proto/azt.proto` - Add UpdateTrustScore RPC
- `azt-framework/azt-gateway/internal/grpc/server.go` - Add Trust Scoring handlers
- `azt-framework/azt-gateway/cmd/gateway/main.go` - Wire up Trust Scoring

## Implementation Phases

### Phase 2.1: Foundation
- PostgreSQL schema and store layer
- Basic GetScore/UpdateScore without factors
- Connect to gRPC server

### Phase 2.2: Factor Evaluation
- Implement all 5 factor calculators
- Unit tests for each factor

### Phase 2.3: Integration
- Connect Trust Scoring to Policy Engine
- Add async communication path
- End-to-end tests
