package shield

import "context"

type Analyzer interface {
	Analyze(ctx context.Context, input *ShieldInput) (*AnalyzerResult, error)
	Name() string
}

type AnalyzerResult struct {
	Analyzer    string   `json:"analyzer"`
	Score       int      `json:"score"`
	Indicators  []string `json:"indicators"`
	MatchedRule string   `json:"matched_rule,omitempty"`
}

type ShieldInput struct {
	AgentID    string                 `json:"agent_id"`
	Action     string                 `json:"action"`
	Tool       string                 `json:"tool"`
	Prompt     string                 `json:"prompt,omitempty"`
	Output     string                 `json:"output,omitempty"`
	Parameters map[string]interface{} `json:"parameters,omitempty"`
	TrustScore int                    `json:"trust_score"`
	Timestamp  int64                  `json:"timestamp"`
}

type ShieldDecision struct {
	Action        string   `json:"action"`
	SeverityScore int      `json:"severity_score"`
	Indicators    []string `json:"indicators"`
	Reason        string   `json:"reason"`
}