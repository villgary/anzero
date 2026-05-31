package shield

import (
	"context"

	"go.uber.org/zap"
)

type Shield struct {
	analyzers  []Analyzer
	aggregator *Aggregator
	logger     *zap.Logger
}

func NewShield(logger *zap.Logger) *Shield {
	analyzers := []Analyzer{
		NewInjectorAnalyzer(nil),
		NewExfiltrationAnalyzer(nil),
		NewAbuseAnalyzer(nil),
	}
	aggregator := NewAggregator(80, 50)
	return &Shield{
		analyzers:  analyzers,
		aggregator: aggregator,
		logger:     logger,
	}
}

func (s *Shield) Evaluate(ctx context.Context, input *ShieldInput) (*ShieldDecision, error) {
	if s.logger != nil {
		s.logger.Info("Evaluating input",
			zap.String("agent_id", input.AgentID),
			zap.String("action", input.Action),
			zap.String("tool", input.Tool),
		)
	}

	// Run all analyzers in parallel
	results := make([]*AnalyzerResult, 0, len(s.analyzers))
	for _, analyzer := range s.analyzers {
		result, err := analyzer.Analyze(ctx, input)
		if err != nil {
			if s.logger != nil {
				s.logger.Warn("Analyzer failed",
					zap.String("analyzer", analyzer.Name()),
					zap.Error(err),
				)
			}
			continue
		}
		results = append(results, result)
	}

	// Aggregate results
	score, action := s.aggregator.Aggregate(results)

	// Collect all indicators
	allIndicators := []string{}
	for _, r := range results {
		allIndicators = append(allIndicators, r.Indicators...)
	}

	decision := &ShieldDecision{
		Action:        action,
		SeverityScore: score,
		Indicators:    allIndicators,
		Reason:        formatReason(action, score, allIndicators),
	}

	if s.logger != nil {
		s.logger.Info("Shield decision",
			zap.String("action", decision.Action),
			zap.Int("score", decision.SeverityScore),
			zap.Strings("indicators", decision.Indicators),
		)
	}

	return decision, nil
}

func formatReason(action string, score int, indicators []string) string {
	switch action {
	case "BLOCK":
		return "Critical threat detected"
	case "LOG_ALERT":
		return "Suspicious activity detected"
	default:
		return "No threats detected"
	}
}
