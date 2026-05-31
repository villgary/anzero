package grpc

import (
	"context"
	"testing"

	"github.com/anzero/azt-framework/azt-gateway/internal/audit"
	"github.com/anzero/azt-framework/azt-gateway/internal/policy"
	"github.com/anzero/azt-framework/azt-gateway/internal/trust"
	v1 "github.com/anzero/azt-framework/proto/azt/v1"
	"go.uber.org/zap"
)

// minimalStore is a stub implementation of trust.Store for testing.
type minimalStore struct {
	scores map[string]*trust.AgentScore
}

func (s *minimalStore) GetScore(ctx context.Context, agentID string) (*trust.AgentScore, error) {
	if score, ok := s.scores[agentID]; ok {
		return score, nil
	}
	return &trust.AgentScore{AgentID: agentID, Score: 70}, nil
}

func (s *minimalStore) UpsertScore(ctx context.Context, agentID string, score int, identityVerified bool, spiffeID string) error {
	if s.scores == nil {
		s.scores = make(map[string]*trust.AgentScore)
	}
	s.scores[agentID] = &trust.AgentScore{AgentID: agentID, Score: score}
	return nil
}

func (s *minimalStore) AddHistory(ctx context.Context, agentID string, prevScore, newScore, delta int, factor, reason string, actionCtx map[string]interface{}) error {
	return nil
}

func (s *minimalStore) GetHistory(ctx context.Context, agentID string, limit int) ([]trust.ScoreHistory, error) {
	return nil, nil
}

func (s *minimalStore) InitSchema(ctx context.Context) error {
	return nil
}

// minimalScorer is a stub implementation of trust.Scorer for testing.
type minimalScorer struct {
	store *minimalStore
}

func (s *minimalScorer) EvaluateAllFactors(ctx context.Context, agentID string, actionCtx map[string]interface{}) (int, trust.FactorBreakdown, []trust.FactorResult, error) {
	return 70, trust.FactorBreakdown{}, nil, nil
}

func TestEnforce_AllowAll(t *testing.T) {
	logger, _ := zap.NewDevelopment()
	store := &minimalStore{scores: make(map[string]*trust.AgentScore)}
	scorer := &minimalScorer{store: store}
	server := NewServer("localhost:0", logger, policy.NewEngine(), audit.NewLogger(logger), scorer, store)

	resp, err := server.Enforce(context.Background(), &v1.EnforcementRequest{
		Context: &v1.ActionContext{
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
	if resp.Decision != v1.Decision_DECISION_ALLOW {
		t.Errorf("Expected ALLOW, got %v", resp.Decision)
	}
	if resp.Reason == "" {
		t.Error("Reason should not be empty")
	}
}

func TestGetTrustScore_Default(t *testing.T) {
	logger, _ := zap.NewDevelopment()
	store := &minimalStore{scores: make(map[string]*trust.AgentScore)}
	scorer := &minimalScorer{store: store}
	server := NewServer("localhost:0", logger, policy.NewEngine(), audit.NewLogger(logger), scorer, store)

	resp, err := server.GetTrustScore(context.Background(), &v1.TrustScoreRequest{
		AgentId: "test-agent",
	})

	if err != nil {
		t.Fatalf("GetTrustScore failed: %v", err)
	}
	if resp.Score != 70 {
		t.Errorf("Expected score 70, got %d", resp.Score)
	}
}
