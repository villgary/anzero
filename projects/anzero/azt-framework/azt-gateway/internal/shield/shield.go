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
	// Placeholder - returns ALLOW
	return &ShieldDecision{
		Action:        "ALLOW",
		SeverityScore: 0,
		Indicators:    []string{},
		Reason:        "No threats detected",
	}, nil
}