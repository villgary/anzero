package audit

import (
	"encoding/json"
	"time"

	"go.uber.org/zap"
)

type AuditEvent struct {
	Timestamp     string `json:"timestamp"`
	EventType     string `json:"event_type"`
	AgentId       string `json:"agent_id"`
	Action        string `json:"action"`
	Tool          string `json:"tool"`
	Decision      string `json:"decision"`
	Reason        string `json:"reason"`
	TrustScore    int    `json:"trust_score"`
	SessionId     string `json:"session_id"`
	RequestId     string `json:"request_id"`
}

type Logger struct {
	logger *zap.Logger
}

func NewLogger(logger *zap.Logger) *Logger {
	return &Logger{logger: logger}
}

func (l *Logger) LogEnforcement(event AuditEvent) {
	event.Timestamp = time.Now().UTC().Format(time.RFC3339)
	event.EventType = "enforcement"
	data, _ := json.Marshal(event)
	l.logger.Info("AUDIT", zap.ByteString("event", data))
}

func (l *Logger) LogTrustScoreChange(agentId string, oldScore, newScore int, reason string) {
	event := map[string]interface{}{
		"timestamp":   time.Now().UTC().Format(time.RFC3339),
		"event_type": "trust_score_change",
		"agent_id":   agentId,
		"old_score":  oldScore,
		"new_score":  newScore,
		"reason":     reason,
	}
	data, _ := json.Marshal(event)
	l.logger.Info("AUDIT", zap.ByteString("event", data))
}
