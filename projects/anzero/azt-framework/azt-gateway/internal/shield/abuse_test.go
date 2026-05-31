package shield

import (
	"context"
	"testing"
	"time"
)

func TestAbuse_DetectsRapidRequests(t *testing.T) {
	abuse := NewAbuseAnalyzer(nil)
	input := &ShieldInput{
		AgentID:  "test-agent",
		Action:   "tool_call",
		Tool:     "search",
		Timestamp: time.Now().Unix(),
	}

	// Simulate rapid requests (>10 in 1 minute triggers rapid_requests indicator)
	for i := 0; i < 11; i++ {
		_, _ = abuse.Analyze(context.Background(), input)
	}

	result, _ := abuse.Analyze(context.Background(), input)
	if result.Score < 30 {
		t.Errorf("Expected score >= 30 for rapid requests, got %d", result.Score)
	}
}

func TestAbuse_DetectsSuspiciousToolSequence(t *testing.T) {
	abuse := NewAbuseAnalyzer(nil)
	input := &ShieldInput{
		AgentID: "test-agent",
		Action:  "tool_call",
		Tool:    "send_email",
		Parameters: map[string]interface{}{
			"previous_tools": []string{"read_file", "delete_file"},
		},
	}

	result, err := abuse.Analyze(context.Background(), input)
	if err != nil {
		t.Fatalf("Analyze failed: %v", err)
	}
	if result.Score < 50 {
		t.Errorf("Expected score >= 50 for suspicious sequence, got %d", result.Score)
	}
}

func TestAbuse_AllowsNormalUsage(t *testing.T) {
	abuse := NewAbuseAnalyzer(nil)
	input := &ShieldInput{
		AgentID: "test-agent",
		Action:  "tool_call",
		Tool:    "search",
	}

	result, err := abuse.Analyze(context.Background(), input)
	if err != nil {
		t.Fatalf("Analyze failed: %v", err)
	}
	if result.Score >= 50 {
		t.Errorf("Expected score < 50 for normal usage, got %d", result.Score)
	}
}