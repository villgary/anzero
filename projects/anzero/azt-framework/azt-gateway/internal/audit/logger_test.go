package audit

import (
	"testing"

	"go.uber.org/zap"
)

func TestLogger_LogEnforcement(t *testing.T) {
	logger, _ := zap.NewDevelopment()
	auditor := NewLogger(logger)

	event := AuditEvent{
		AgentId:   "test-agent",
		Action:    "tool_call",
		Tool:      "read",
		Decision:  "allow",
		Reason:    "Allowed by rule: allow-read",
		TrustScore: 70,
		SessionId: "session-123",
		RequestId: "req-456",
	}

	auditor.LogEnforcement(event)
}

func TestLogger_LogTrustScoreChange(t *testing.T) {
	logger, _ := zap.NewDevelopment()
	auditor := NewLogger(logger)
	auditor.LogTrustScoreChange("test-agent", 70, 65, "Suspicious pattern detected")
}
