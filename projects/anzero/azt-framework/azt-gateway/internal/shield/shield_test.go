package shield

import (
	"context"
	"testing"
)

func TestShield_Evaluate_NoThreats(t *testing.T) {
	shield := NewShield(nil, nil, nil)
	input := &ShieldInput{
		AgentID: "test-agent",
		Action:  "tool_call",
		Tool:    "read_file",
		Prompt:  "Show me the contents of /etc/passwd",
	}

	decision, err := shield.Evaluate(context.Background(), input)
	if err != nil {
		t.Fatalf("Evaluate failed: %v", err)
	}
	if decision.Action != "ALLOW" {
		t.Errorf("Expected ALLOW, got %s", decision.Action)
	}
}