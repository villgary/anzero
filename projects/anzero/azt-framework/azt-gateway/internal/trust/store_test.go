// internal/trust/store_test.go
package trust

import (
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
		"tool":   "read",
		"action": "tool_call",
	}
	if ctx["tool"] != "read" {
		t.Errorf("expected tool=read, got %v", ctx["tool"])
	}
}
