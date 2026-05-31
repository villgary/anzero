package policy

import (
	"os"
	"testing"

	v1 "github.com/anzero/azt-framework/proto/azt/v1"
)

func TestEngine_Evaluate_AllowByDefault(t *testing.T) {
	engine := NewEngine()
	ctx := &v1.ActionContext{
		AgentId:    "unknown-agent",
		Action:     "tool_call",
		Tool:       "some_tool",
		TrustScore: 70,
	}
	decision, reason := engine.Evaluate(ctx)
	if decision != v1.Decision_DECISION_ALLOW {
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

	ctx := &v1.ActionContext{
		AgentId:    "test-agent",
		Action:     "tool_call",
		Tool:       "read",
		TrustScore: 70,
	}
	decision, reason := engine.Evaluate(ctx)
	if decision != v1.Decision_DECISION_ALLOW {
		t.Errorf("Expected ALLOW for read tool, got %v", decision)
	}
	t.Logf("Allow reason: %s", reason)

	ctx.Tool = "delete"
	decision, reason = engine.Evaluate(ctx)
	if decision != v1.Decision_DECISION_DENY {
		t.Errorf("Expected DENY for delete tool, got %v", decision)
	}
	t.Logf("Deny reason: %s", reason)
}