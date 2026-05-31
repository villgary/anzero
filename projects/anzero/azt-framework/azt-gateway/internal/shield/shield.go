package shield

import (
	"context"
	"go.uber.org/zap"
)

// Aggregator is a placeholder type that will be defined in Task 2
// when the Severity Aggregator is implemented.
type Aggregator struct{}

type Shield struct {
	analyzers  []Analyzer
	aggregator *Aggregator
	logger     *zap.Logger
}

func NewShield(analyzers []Analyzer, aggregator *Aggregator, logger *zap.Logger) *Shield {
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