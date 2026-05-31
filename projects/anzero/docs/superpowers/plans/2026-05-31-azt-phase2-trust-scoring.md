# Phase 2: Trust Scoring Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement Trust Scoring service with five-factor evaluation and PostgreSQL persistence, integrated with Policy Engine.

**Architecture:** Trust Scoring Service runs inside Go Gateway, stores scores in PostgreSQL, evaluates 5 factors per action, and feeds scores into Policy Engine decisions.

**Tech Stack:** Go 1.21+, PostgreSQL 14+, pgx driver, gRPC

---

## File Structure

```
azt-framework/
├── azt-gateway/
│   ├── internal/
│   │   ├── trust/
│   │   │   ├── scorer.go       # Main scoring logic
│   │   │   ├── scorer_test.go
│   │   │   ├── store.go        # PostgreSQL storage
│   │   │   ├── store_test.go
│   │   │   ├── analyzer.go     # Anomaly detection
│   │   │   └── analyzer_test.go
│   │   ├── grpc/
│   │   │   └── server.go      # Updated with trust handlers
│   │   └── policy/
│   │       └── engine.go       # Updated with trust scoring
│   ├── migrations/
│   │   └── 001_create_trust_tables.sql
│   └── cmd/gateway/main.go     # Updated to wire trust scoring
├── proto/
│   └── azt.proto               # Updated with trust RPCs
└── azt-sdk-python/
    └── azt/
        └── client.py          # Updated with trust score methods
```

---

## Task 1: PostgreSQL Schema and Store Layer

**Files:**
- Create: `azt-framework/azt-gateway/migrations/001_create_trust_tables.sql`
- Create: `azt-framework/azt-gateway/internal/trust/store.go`
- Create: `azt-framework/azt-gateway/internal/trust/store_test.go`

- [ ] **Step 1: Create SQL migration**

```sql
-- 001_create_trust_tables.sql
CREATE TABLE IF NOT EXISTS agent_scores (
    agent_id VARCHAR(255) PRIMARY KEY,
    score INTEGER NOT NULL DEFAULT 70 CHECK (score >= 0 AND score <= 100),
    identity_verified BOOLEAN DEFAULT FALSE,
    spiffe_id VARCHAR(512),
    last_action_at TIMESTAMP,
    last_updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS score_history (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(255) NOT NULL REFERENCES agent_scores(agent_id) ON DELETE CASCADE,
    previous_score INTEGER NOT NULL,
    new_score INTEGER NOT NULL,
    delta INTEGER NOT NULL,
    factor VARCHAR(50) NOT NULL,
    reason TEXT,
    action_context JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_score_history_agent_id ON score_history(agent_id);
CREATE INDEX IF NOT EXISTS idx_score_history_created_at ON score_history(created_at);
```

- [ ] **Step 2: Create store.go**

```go
// internal/trust/store.go
package trust

import (
    "context"
    "encoding/json"
    "fmt"
    ""time"

    "github.com/jackc/pgx/v5"
    "github.com/jackc/pgx/v5/pgxpool"
)

type AgentScore struct {
    AgentID          string
    Score            int
    IdentityVerified bool
    SPIFFEID         string
    LastActionAt     time.Time
    LastUpdatedAt    time.Time
}

type ScoreHistory struct {
    ID              int
    AgentID         string
    PreviousScore   int
    NewScore        int
    Delta           int
    Factor          string
    Reason          string
    ActionContext   map[string]interface{}
    CreatedAt       time.Time
}

type ActionContextJSON map[string]interface{}

type Store struct {
    pool *pgxpool.Pool
}

func NewStore(pool *pgxpool.Pool) *Store {
    return &Store{pool: pool}
}

func (s *Store) InitSchema(ctx context.Context) error {
    schema := `
    CREATE TABLE IF NOT EXISTS agent_scores (
        agent_id VARCHAR(255) PRIMARY KEY,
        score INTEGER NOT NULL DEFAULT 70 CHECK (score >= 0 AND score <= 100),
        identity_verified BOOLEAN DEFAULT FALSE,
        spiffe_id VARCHAR(512),
        last_action_at TIMESTAMP,
        last_updated_at TIMESTAMP DEFAULT NOW()
    );
    CREATE TABLE IF NOT EXISTS score_history (
        id SERIAL PRIMARY KEY,
        agent_id VARCHAR(255) NOT NULL REFERENCES agent_scores(agent_id) ON DELETE CASCADE,
        previous_score INTEGER NOT NULL,
        new_score INTEGER NOT NULL,
        delta INTEGER NOT NULL,
        factor VARCHAR(50) NOT NULL,
        reason TEXT,
        action_context JSONB,
        created_at TIMESTAMP DEFAULT NOW()
    );
    CREATE INDEX IF NOT EXISTS idx_score_history_agent_id ON score_history(agent_id);
    CREATE INDEX IF NOT EXISTS idx_score_history_created_at ON score_history(created_at);
    `
    _, err := s.pool.Exec(ctx, schema)
    return err
}

func (s *Store) GetScore(ctx context.Context, agentID string) (*AgentScore, error) {
    row := s.pool.QueryRow(ctx,
        "SELECT agent_id, score, identity_verified, COALESCE(spiffe_id, ''), last_action_at, last_updated_at FROM agent_scores WHERE agent_id = $1",
        agentID)
    var score AgentScore
    var lastAction, lastUpdated pgx.NullTime
    err := row.Scan(&score.AgentID, &score.Score, &score.IdentityVerified, &score.SPIFFEID, &lastAction, &lastUpdated)
    if err == pgx.ErrNoRows {
        return &AgentScore{
            AgentID: agentID,
            Score:   70,
        }, nil
    }
    if err != nil {
        return nil, fmt.Errorf("failed to get score: %w", err)
    }
    score.LastActionAt = lastAction.Time
    score.LastUpdatedAt = lastUpdated.Time
    return &score, nil
}

func (s *Store) UpsertScore(ctx context.Context, agentID string, score int, identityVerified bool, spiffeID string) error {
    _, err := s.pool.Exec(ctx, `
        INSERT INTO agent_scores (agent_id, score, identity_verified, spiffe_id, last_action_at, last_updated_at)
        VALUES ($1, $2, $3, $4, NOW(), NOW())
        ON CONFLICT (agent_id) DO UPDATE SET
            score = EXCLUDED.score,
            identity_verified = EXCLUDED.identity_verified,
            spiffe_id = EXCLUDED.spiffe_id,
            last_action_at = NOW(),
            last_updated_at = NOW()
    `, agentID, score, identityVerified, spiffeID)
    return err
}

func (s *Store) AddHistory(ctx context.Context, agentID string, prevScore, newScore, delta int, factor, reason string, actionCtx map[string]interface{}) error {
    ctxJSON, err := json.Marshal(actionCtx)
    if err != nil {
        return fmt.Errorf("failed to marshal action context: %w", err)
    }
    _, err = s.pool.Exec(ctx, `
        INSERT INTO score_history (agent_id, previous_score, new_score, delta, factor, reason, action_context)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
    `, agentID, prevScore, newScore, delta, factor, reason, ctxJSON)
    return err
}

func (s *Store) GetHistory(ctx context.Context, agentID string, limit int) ([]ScoreHistory, error) {
    rows, err := s.pool.Query(ctx, `
        SELECT id, agent_id, previous_score, new_score, delta, factor, reason, action_context, created_at
        FROM score_history
        WHERE agent_id = $1
        ORDER BY created_at DESC
        LIMIT $2
    `, agentID, limit)
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    var history []ScoreHistory
    for rows.Next() {
        var h ScoreHistory
        var reasonNull *string
        var ctxJSON []byte
        var createdAt pgx.NullTime
        err := rows.Scan(&h.ID, &h.AgentID, &h.PreviousScore, &h.NewScore, &h.Delta, &h.Factor, &reasonNull, &ctxJSON, &createdAt)
        if err != nil {
            return nil, err
        }
        if reasonNull != nil {
            h.Reason = *reasonNull
        }
        if ctxJSON != nil {
            json.Unmarshal(ctxJSON, &h.ActionContext)
        }
        h.CreatedAt = createdAt.Time
        history = append(history, h)
    }
    return history, nil
}
```

- [ ] **Step 3: Create store_test.go**

```go
// internal/trust/store_test.go
package trust

import (
    "context"
    "testing"
)

func TestAgentScore_Defaults(t *testing.T) {
    score := &AgentScore{
        AgentID: "test-agent",
        Score:   70,
    }
    if score.Score != 70 {
        t.Errorf("expected default score 70, got %d", score.Score)
    }
}

func TestActionContextJSON_Marshal(t *testing.T) {
    ctx := ActionContextJSON{
        "tool":  "read",
        "action": "tool_call",
    }
    if ctx["tool"] != "read" {
        t.Errorf("expected tool=read, got %v", ctx["tool"])
    }
}
```

- [ ] **Step 4: Run tests**

Run: `cd azt-framework/azt-gateway && go test ./internal/trust/... -v`
Expected: PASS

- [ ] **Step 5: Update go.mod with PostgreSQL dependency**

Run: `cd azt-framework/azt-gateway && go get github.com/jackc/pgx/v5@latest && go get github.com/jackc/pgx/v5/pgxpool@latest && go mod tidy`

- [ ] **Step 6: Commit**

```bash
git add azt-framework/azt-gateway/migrations/ azt-framework/azt-gateway/internal/trust/store.go azt-framework/azt-gateway/internal/trust/store_test.go azt-framework/azt-gateway/go.mod azt-framework/azt-gateway/go.sum
git commit -m "feat(gateway): add PostgreSQL store layer for trust scoring
- Add schema migration for agent_scores and score_history tables
- Add Store with GetScore, UpsertScore, AddHistory, GetHistory methods
- Add pgx driver for PostgreSQL
- Add unit tests

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Task 2: Implement Five-Factor Scoring

**Files:**
- Create: `azt-framework/azt-gateway/internal/trust/scorer.go`
- Create: `azt-framework/azt-gateway/internal/trust/scorer_test.go`

- [ ] **Step 1: Create scorer.go with all 5 factors**

```go
// internal/trust/scorer.go
package trust

import (
    "math"
    "time"
)

const (
    FactorIdentity    = "identity"
    FactorHistory    = "history"
    FactorTimeOfDay  = "time_of_day"
    FactorAnomaly    = "anomaly"
    FactorFrequency  = "frequency"
)

type FactorResult struct {
    Factor   string
    Score    int
    Delta    int
    Reason   string
}

type FactorBreakdown struct {
    Identity int
    History  int
    Time     int
    Anomaly  int
    Frequency int
}

type Scorer struct {
    store *Store
}

func NewScorer(store *Store) *Scorer {
    return &Scorer{store: store}
}

func (s *Scorer) EvaluateAllFactors(ctx context.Context, agentID string, actionCtx map[string]interface{}) (int, FactorBreakdown, []FactorResult, error) {
    agentScore, err := s.store.GetScore(ctx, agentID)
    if err != nil {
        return 70, FactorBreakdown{}, nil, err
    }

    var results []FactorResult
    var totalDelta int

    // Factor 1: Identity (20%)
    identityResult := s.evaluateIdentity(agentScore)
    results = append(results, identityResult)
    totalDelta += identityResult.Delta

    // Factor 2: Historical (25%)
    historyResult, err := s.evaluateHistory(ctx, agentScore)
    if err == nil {
        results = append(results, historyResult)
        totalDelta += historyResult.Delta
    }

    // Factor 3: Time of Day (15%)
    timeResult := s.evaluateTimeOfDay(agentScore)
    results = append(results, timeResult)
    totalDelta += timeResult.Delta

    // Factor 4: Anomaly (20%) - placeholder for Phase 3
    anomalyResult := s.evaluateAnomaly(actionCtx, agentScore)
    results = append(results, anomalyResult)
    totalDelta += anomalyResult.Delta

    // Factor 5: Tool Frequency (20%) - placeholder for Phase 3
    freqResult := s.evaluateFrequency(actionCtx, agentScore)
    results = append(results, freqResult)
    totalDelta += freqResult.Delta

    newScore := clamp(agentScore.Score+totalDelta, 0, 100)

    breakdown := FactorBreakdown{
        Identity:  identityResult.Score,
        History:   historyResult.Score,
        Time:      timeResult.Score,
        Anomaly:   anomalyResult.Score,
        Frequency: freqResult.Score,
    }

    return newScore, breakdown, results, nil
}

func (s *Scorer) evaluateIdentity(score *AgentScore) FactorResult {
    if score.IdentityVerified {
        return FactorResult{
            Factor: FactorIdentity,
            Score:   100,
            Delta:   0,
            Reason:  "SPIFFE identity verified",
        }
    }
    if score.SPIFFEID == "" {
        return FactorResult{
            Factor: FactorIdentity,
            Score:   50,
            Delta:   0,
            Reason:  "No SPIFFE ID present",
        }
    }
    return FactorResult{
        Factor: FactorIdentity,
        Score:   30,
        Delta:   -10,
        Reason:  "SPIFFE ID present but not verified",
    }
}

func (s *Scorer) evaluateHistory(ctx context.Context, score *AgentScore) (FactorResult, error) {
    history, err := s.store.GetHistory(ctx, score.AgentID, 100)
    if err != nil || len(history) == 0 {
        return FactorResult{
            Factor: FactorHistory,
            Score:   70,
            Delta:   0,
            Reason:  "No history yet",
        }, err
    }

    denyCount := 0
    for _, h := range history {
        if h.NewScore < h.PreviousScore {
            denyCount++
        }
    }
    denyRatio := float64(denyCount) / float64(len(history))

    if denyRatio > 0.5 {
        return FactorResult{
            Factor: FactorHistory,
            Score:   25,
            Delta:   -25,
            Reason:  "High denial ratio",
        }, nil
    }
    if denyRatio > 0.2 {
        return FactorResult{
            Factor: FactorHistory,
            Score:   55,
            Delta:   -15,
            Reason:  "Moderate denial ratio",
        }, nil
    }
    return FactorResult{
        Factor: FactorHistory,
        Score:   85,
        Delta:   5,
        Reason:  "Good behavioral history",
    }, nil
}

func (s *Scorer) evaluateTimeOfDay(score *AgentScore) FactorResult {
    hour := time.Now().Hour()
    // Typical business hours: 9am-6pm
    if hour >= 9 && hour <= 18 {
        return FactorResult{
            Factor: FactorTimeOfDay,
            Score:   100,
            Delta:   5,
            Reason:  "Access during business hours",
        }
    }
    return FactorResult{
        Factor: FactorTimeOfDay,
        Score:   60,
        Delta:   -10,
        Reason:  "Access outside business hours",
    }
}

func (s *Scorer) evaluateAnomaly(ctx map[string]interface{}, score *AgentScore) FactorResult {
    // Phase 3 will implement full anomaly detection
    return FactorResult{
        Factor: FactorAnomaly,
        Score:   70,
        Delta:   0,
        Reason:  "No anomalies detected (Phase 2 placeholder)",
    }
}

func (s *Scorer) evaluateFrequency(ctx map[string]interface{}, score *AgentScore) FactorResult {
    // Phase 3 will implement frequency analysis
    return FactorResult{
        Factor: FactorFrequency,
        Score:   70,
        Delta:   0,
        Reason:  "Normal tool usage (Phase 2 placeholder)",
    }
}

func clamp(val, min, max int) int {
    return int(math.Max(float64(min), math.Min(float64(max), float64(val))))
}
```

- [ ] **Step 2: Create scorer_test.go**

```go
// internal/trust/scorer_test.go
package trust

import (
    "testing"
)

func TestClamp(t *testing.T) {
    tests := []struct {
        val, min, max int
        expected      int
    }{
        {50, 0, 100, 50},
        {-10, 0, 100, 0},
        {150, 0, 100, 100},
    }
    for _, tt := range tests {
        result := clamp(tt.val, tt.min, tt.max)
        if result != tt.expected {
            t.Errorf("clamp(%d, %d, %d) = %d; want %d", tt.val, tt.min, tt.max, result, tt.expected)
        }
    }
}

func TestFactorResult_Identity(t *testing.T) {
    scorer := &Scorer{}
    result := scorer.evaluateIdentity(&AgentScore{AgentID: "test", IdentityVerified: true})
    if result.Score != 100 {
        t.Errorf("expected verified identity score 100, got %d", result.Score)
    }
    if result.Delta != 0 {
        t.Errorf("expected delta 0, got %d", result.Delta)
    }
}

func TestFactorResult_IdentityUnverified(t *testing.T) {
    scorer := &Scorer{}
    result := scorer.evaluateIdentity(&AgentScore{AgentID: "test", IdentityVerified: false})
    if result.Score != 50 {
        t.Errorf("expected unverified identity score 50, got %d", result.Score)
    }
}

func TestFactorResult_TimeOfDay(t *testing.T) {
    scorer := &Scorer{}
    result := scorer.evaluateTimeOfDay(&AgentScore{})
    if result.Factor != FactorTimeOfDay {
        t.Errorf("expected factor %s, got %s", FactorTimeOfDay, result.Factor)
    }
}

func TestFactorResult_Anomaly(t *testing.T) {
    scorer := &Scorer{}
    result := scorer.evaluateAnomaly(map[string]interface{}{"tool": "read"}, &AgentScore{})
    if result.Factor != FactorAnomaly {
        t.Errorf("expected factor %s, got %s", FactorAnomaly, result.Factor)
    }
    if result.Score != 70 {
        t.Errorf("expected placeholder score 70, got %d", result.Score)
    }
}

func TestFactorResult_Frequency(t *testing.T) {
    scorer := &Scorer{}
    result := scorer.evaluateFrequency(map[string]interface{}{"tool": "read"}, &AgentScore{})
    if result.Factor != FactorFrequency {
        t.Errorf("expected factor %s, got %s", FactorFrequency, result.Factor)
    }
}
```

- [ ] **Step 3: Run tests**

Run: `cd azt-framework/azt-gateway && go test ./internal/trust/... -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add azt-framework/azt-gateway/internal/trust/scorer.go azt-framework/azt-gateway/internal/trust/scorer_test.go
git commit -m "feat(gateway): add five-factor trust scoring
- Implement identity, history, time-of-day, anomaly, frequency factors
- Add FactorResult and FactorBreakdown types
- Add clamp utility function
- Add unit tests for all factors

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Task 3: Update Proto and gRPC Server

**Files:**
- Modify: `azt-framework/proto/azt.proto`
- Modify: `azt-framework/azt-gateway/internal/grpc/server.go`
- Modify: `azt-framework/azt-gateway/cmd/gateway/main.go`

- [ ] **Step 1: Update azt.proto with trust scoring RPCs**

```protobuf
// Add to azt.proto
message UpdateTrustScoreRequest {
  string agent_id = 1;
  string factor = 2;
  int32 delta = 3;
  string reason = 4;
  map<string, string> action_context = 5;
}

message GetAgentScoreRequest {
  string agent_id = 1;
}

message FactorBreakdown {
  int32 identity = 1;
  int32 history = 2;
  int32 time = 3;
  int32 anomaly = 4;
  int32 frequency = 5;
}

message TrustScoreResponse {
  int32 score = 1;
  string reason = 2;
  FactorBreakdown breakdown = 3;
  string agent_id = 4;
}

service AZTGateway {
  rpc Enforce(EnforcementRequest) returns (EnforcementResponse);
  rpc GetTrustScore(TrustScoreRequest) returns (TrustScoreResponse);
  rpc UpdateTrustScore(UpdateTrustScoreRequest) returns (TrustScoreResponse);
  rpc GetAgentScore(GetAgentScoreRequest) returns (TrustScoreResponse);
}
```

- [ ] **Step 2: Regenerate Go gRPC code**

Run: `cd azt-framework && go install google.golang.org/protobuf/cmd/protoc-gen-go@v1.32.0 && go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@v1.3.0`
Run: `cd azt-framework && export PATH="$PATH:$(go env GOPATH)/bin" && protoc --go_out=. --go_opt=paths=source_relative --go-grpc_out=. --go-grpc_opt=paths=source_relative proto/azt.proto`

- [ ] **Step 3: Regenerate Python gRPC code**

Run: `cd azt-framework && python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. proto/azt.proto`

- [ ] **Step 4: Update gRPC server with trust handlers**

```go
// internal/grpc/server.go (updated)
package grpc

import (
    "context"

    "github.com/anzero/azt-framework/azt-gateway/internal/audit"
    "github.com/anzero/azt-framework/azt-gateway/internal/policy"
    "github.com/anzero/azt-framework/azt-gateway/internal/trust"
    "github.com/anzero/azt-framework/proto/azt/v1"
    "go.uber.org/zap"
)

type Server struct {
    addr   string
    logger *zap.Logger
    engine *policy.Engine
    audit  *audit.Logger
    scorer *trust.Scorer
    store  *trust.Store
    azt.UnimplementedAZTGatewayServer
}

func NewServer(addr string, logger *zap.Logger, engine *policy.Engine, auditLogger *audit.Logger, scorer *trust.Scorer, store *trust.Store) *Server {
    return &Server{
        addr:   addr,
        logger: logger,
        engine: engine,
        audit:  auditLogger,
        scorer: scorer,
        store:  store,
    }
}

func (s *Server) Enforce(ctx context.Context, req *azt.EnforcementRequest) (*azt.EnforcementResponse, error) {
    s.logger.Info("Enforce request received",
        zap.String("agent_id", req.Context.AgentId),
        zap.String("action", req.Context.Action),
        zap.String("tool", req.Context.Tool),
    )

    // Get trust score from store
    agentScore, err := s.store.GetScore(ctx, req.Context.AgentId)
    if err != nil {
        s.logger.Warn("Failed to get trust score", zap.Error(err))
    }
    req.Context.TrustScore = int32(agentScore.Score)

    decision, reason := s.engine.Evaluate(req.Context)

    s.audit.LogEnforcement(audit.AuditEvent{
        AgentId:    req.Context.AgentId,
        Action:     req.Context.Action,
        Tool:       req.Context.Tool,
        Decision:   decision.String(),
        Reason:     reason,
        TrustScore: agentScore.Score,
        SessionId:  req.Context.SessionId,
    })

    return &azt.EnforcementResponse{
        Decision:          decision,
        Reason:            reason,
        UpdatedTrustScore: int32(agentScore.Score),
    }, nil
}

func (s *Server) GetTrustScore(ctx context.Context, req *azt.TrustScoreRequest) (*azt.TrustScoreResponse, error) {
    agentScore, err := s.store.GetScore(ctx, req.AgentId)
    if err != nil {
        return nil, err
    }
    return &azt.TrustScoreResponse{
        Score:   int32(agentScore.Score),
        Reason:  "Current trust score",
        AgentId: agentScore.AgentID,
    }, nil
}

func (s *Server) UpdateTrustScore(ctx context.Context, req *azt.UpdateTrustScoreRequest) (*azt.TrustScoreResponse, error) {
    agentScore, err := s.store.GetScore(ctx, req.AgentId)
    if err != nil {
        agentScore = &trust.AgentScore{AgentID: req.AgentId, Score: 70}
    }

    newScore, breakdown, results, err := s.scorer.EvaluateAllFactors(ctx, req.AgentId, req.ActionContext)
    if err != nil {
        return nil, err
    }

    // Persist
    s.store.UpsertScore(ctx, req.AgentId, newScore, false, "")

    // Log history
    delta := newScore - agentScore.Score
    s.store.AddHistory(ctx, req.AgentId, agentScore.Score, newScore, delta, req.Factor, req.Reason, req.ActionContext)

    return &azt.TrustScoreResponse{
        Score:    int32(newScore),
        Reason:   req.Reason,
        Breakdown: &azt.FactorBreakdown{
            Identity: int32(breakdown.Identity),
            History:  int32(breakdown.History),
            Time:     int32(breakdown.Time),
            Anomaly:  int32(breakdown.Anomaly),
            Frequency: int32(breakdown.Frequency),
        },
        AgentId: req.AgentId,
    }, nil
}

func (s *Server) GetAgentScore(ctx context.Context, req *azt.GetAgentScoreRequest) (*azt.TrustScoreResponse, error) {
    return s.UpdateTrustScore(ctx, &azt.UpdateTrustScoreRequest{
        AgentId: req.AgentId,
    })
}
```

- [ ] **Step 5: Update main.go to wire trust scoring**

```go
// cmd/gateway/main.go (updated)
func main() {
    addr := flag.String("addr", "localhost:50051", "gRPC server address")
    dbURL := flag.String("db-url", "postgres://localhost:5432/azt?sslmode=disable", "PostgreSQL connection URL")
    flag.Parse()

    config := zap.NewProductionConfig()
    config.EncoderConfig.TimeKey = "timestamp"
    config.EncoderConfig.EncodeTime = zapcore.ISO8601TimeEncoder
    logger, _ := config.Build()

    // Initialize PostgreSQL connection pool
    pool, err := pgxpool.New(context.Background(), *dbURL)
    if err != nil {
        logger.Fatal("Failed to create connection pool", zap.Error(err))
    }
    defer pool.Close()

    // Run migrations
    store := trust.NewStore(pool)
    if err := store.InitSchema(context.Background()); err != nil {
        logger.Fatal("Failed to initialize schema", zap.Error(err))
    }

    // Initialize services
    engine := policy.NewEngine()
    auditLogger := audit.NewLogger(logger)
    scorer := trust.NewScorer(store)

    // Load policies if path provided
    if policyPath := os.Getenv("AZT_POLICY_PATH"); policyPath != "" {
        if err := engine.LoadPolicy(policyPath, "default"); err != nil {
            logger.Warn("Failed to load policy", zap.Error(err))
        }
    }

    server := grpc.NewServer(*addr, logger, engine, auditLogger, scorer, store)
    logger.Info(fmt.Sprintf("Starting AZT Gateway on %s", *addr))
    if err := server.Start(); err != nil {
        logger.Fatal("Failed to start server", zap.Error(err))
    }
}
```

- [ ] **Step 6: Commit**

```bash
git add azt-framework/proto/ azt-framework/azt-gateway/internal/grpc/server.go azt-framework/azt-gateway/cmd/gateway/main.go
git commit -m "feat(gateway): integrate trust scoring into gRPC server
- Add UpdateTrustScore and GetAgentScore handlers
- Connect scorer to Enforce handler
- Wire store and scorer in main.go
- Update proto with trust RPCs

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Task 4: Update Python SDK with Trust Methods

**Files:**
- Modify: `azt-framework/azt-sdk-python/azt/client.py`

- [ ] **Step 1: Update Python client with trust methods**

```python
# azt/client.py (updated)
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
    update_trust_score_request_pb2 as pb2_update,
    get_agent_score_request_pb2 as pb2_get_score,
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

    def update_trust_score(self, agent_id: str, factor: str, delta: int, reason: str, action_context: dict = None) -> dict:
        req = pb2_update.UpdateTrustScoreRequest(
            agent_id=agent_id,
            factor=factor,
            delta=delta,
            reason=reason,
            action_context=action_context or {},
        )
        resp = self.stub.UpdateTrustScore(req, timeout=self.config.timeout_seconds)
        return {
            "score": resp.score,
            "reason": resp.reason,
            "agent_id": resp.agent_id,
            "breakdown": {
                "identity": resp.breakdown.identity,
                "history": resp.breakdown.history,
                "time": resp.breakdown.time,
                "anomaly": resp.breakdown.anomaly,
                "frequency": resp.breakdown.frequency,
            } if resp.breakdown else None,
        }

    def close(self):
        self.channel.close()
```

- [ ] **Step 2: Commit**

```bash
git add azt-framework/azt-sdk-python/azt/client.py
git commit -m "feat(sdk): add trust scoring methods to Python client
- Add update_trust_score method
- Add get_agent_score method
- Add FactorBreakdown parsing

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Task 5: End-to-End Test and Documentation

**Files:**
- Modify: `azt-framework/README.md`

- [ ] **Step 1: Update README with Phase 2 features**

```markdown
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
score, reason = client.get_trust_score("my-agent")
print(f"Score: {score}, Reason: {reason}")

# Update trust score with action context
result = client.update_trust_score(
    agent_id="my-agent",
    factor="history",
    delta=-10,
    reason="Policy denial",
    action_context={"tool": "delete", "action": "tool_call"}
)
print(f"New score: {result['score']}")
print(f"Breakdown: {result['breakdown']}")
```
```

- [ ] **Step 2: Commit**

```bash
git add azt-framework/README.md
git commit -m "docs: add Phase 2 trust scoring documentation
- Document five-factor scoring
- Add database setup instructions
- Add Python SDK trust scoring examples

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```
