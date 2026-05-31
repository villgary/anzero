package grpc

import (
	"context"
	"testing"

	v1 "github.com/anzero/azt-framework/proto/azt/v1"
	"go.uber.org/zap"
)

func TestEnforce_AllowAll(t *testing.T) {
	logger, _ := zap.NewDevelopment()
	server := NewServer("localhost:0", logger)

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
	server := NewServer("localhost:0", logger)

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
