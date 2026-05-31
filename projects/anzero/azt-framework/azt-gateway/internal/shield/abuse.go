package shield

import (
	"context"
	"regexp"
	"time"
)

type AbuseAnalyzer struct {
	recentRequests      map[string][]time.Time
	suspiciousSequences [][]string
}

func NewAbuseAnalyzer(config interface{}) *AbuseAnalyzer {
	return &AbuseAnalyzer{
		recentRequests: make(map[string][]time.Time),
		suspiciousSequences: [][]string{
			{"read_file", "delete_file", "send_email"},
			{"get_database", "export_data", "post_message"},
		},
	}
}

func (a *AbuseAnalyzer) Name() string {
	return "model_abuse"
}

func (a *AbuseAnalyzer) Analyze(ctx context.Context, input *ShieldInput) (*AnalyzerResult, error) {
	result := &AnalyzerResult{
		Analyzer:   a.Name(),
		Score:      0,
		Indicators: []string{},
	}

	// Check rate limiting
	agentRequests := a.recentRequests[input.AgentID]
	now := time.Now()
	cutoff := now.Add(-1 * time.Minute)

	recent := make([]time.Time, 0)
	for _, t := range agentRequests {
		if t.After(cutoff) {
			recent = append(recent, t)
		}
	}
	recent = append(recent, now)
	a.recentRequests[input.AgentID] = recent

	if len(recent) > 10 {
		result.Indicators = append(result.Indicators, "rapid_requests")
		result.Score = min(result.Score+40, 100)
	} else if len(recent) > 5 {
		result.Indicators = append(result.Indicators, "elevated_request_rate")
		result.Score = min(result.Score+20, 100)
	}

	// Check suspicious tool sequences
	if prevTools, ok := input.Parameters["previous_tools"].([]string); ok {
		for _, seq := range a.suspiciousSequences {
			if a.matchesSequence(append(prevTools, input.Tool), seq) {
				result.Indicators = append(result.Indicators, "suspicious_sequence")
				result.Score = min(result.Score+60, 100)
				break
			}
		}
	}

	// Check for token amplification patterns in prompt
	if input.Prompt != "" {
		largeRepeat := regexp.MustCompile(`(?i)(repeat|loop).{0,20}(this|that|again)`)
		if largeRepeat.MatchString(input.Prompt) {
			result.Indicators = append(result.Indicators, "token_amplification")
			result.Score = min(result.Score+30, 100)
		}
	}

	return result, nil
}

func (a *AbuseAnalyzer) matchesSequence(actual, expected []string) bool {
	if len(actual) < len(expected) {
		return false
	}
	start := len(actual) - len(expected)
	for i := range expected {
		if actual[start+i] != expected[i] {
			return false
		}
	}
	return true
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}