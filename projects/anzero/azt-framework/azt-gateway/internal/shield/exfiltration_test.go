package shield

import (
    "context"
    "testing"
)

func TestExfil_DetectsAPIKey(t *testing.T) {
    exfil := NewExfiltrationAnalyzer(nil)
    input := &ShieldInput{
        AgentID: "test-agent",
        Action:  "tool_call",
        Tool:    "send_email",
        Output:  "Here is the API key: sk-1234567890abcdefghijklmnopqrstuvwxyz",
    }

    result, err := exfil.Analyze(context.Background(), input)
    if err != nil {
        t.Fatalf("Analyze failed: %v", err)
    }
    if result.Score < 80 {
        t.Errorf("Expected score >= 80 for API key, got %d", result.Score)
    }
}

func TestExfil_DetectsSSN(t *testing.T) {
    exfil := NewExfiltrationAnalyzer(nil)
    input := &ShieldInput{
        AgentID: "test-agent",
        Action:  "tool_call",
        Tool:    "export_data",
        Output:  "User SSN: 123-45-6789",
    }

    result, err := exfil.Analyze(context.Background(), input)
    if err != nil {
        t.Fatalf("Analyze failed: %v", err)
    }
    if result.Score < 60 {
        t.Errorf("Expected score >= 60 for SSN, got %d", result.Score)
    }
}

func TestExfil_AllowsNormalOutput(t *testing.T) {
    exfil := NewExfiltrationAnalyzer(nil)
    input := &ShieldInput{
        AgentID: "test-agent",
        Action:  "tool_call",
        Tool:    "search",
        Output:  "The search returned 42 results",
    }

    result, err := exfil.Analyze(context.Background(), input)
    if err != nil {
        t.Fatalf("Analyze failed: %v", err)
    }
    if result.Score >= 50 {
        t.Errorf("Expected score < 50 for normal output, got %d", result.Score)
    }
}