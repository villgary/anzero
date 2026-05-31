package trust

import (
	"context"
	"math"
	"time"
)

const (
	FactorIdentity   = "identity"
	FactorHistory    = "history"
	FactorTimeOfDay  = "time_of_day"
	FactorAnomaly    = "anomaly"
	FactorFrequency  = "frequency"
)

type FactorResult struct {
	Factor string
	Score  int
	Delta  int
	Reason string
}

type FactorBreakdown struct {
	Identity  int
	History   int
	Time      int
	Anomaly   int
	Frequency int
}

type Scorer struct {
	store *Store
}

func NewScorer(store *Store) *Scorer {
	return &Scorer{store: store}
}

func (s *Scorer) EvaluateAllFactors(ctx context.Context, agentID string, actionCtx map[string]interface{}) (int, FactorBreakdown, []FactorResult, error) {
	agentScore, err := s.store.GetScore(ctx, agentID)
	if err != nil {
		return 70, FactorBreakdown{}, nil, err
	}

	var results []FactorResult
	var totalDelta int

	// Factor 1: Identity (20%)
	identityResult := s.evaluateIdentity(agentScore)
	results = append(results, identityResult)
	totalDelta += identityResult.Delta

	// Factor 2: Historical (25%)
	historyResult, err := s.evaluateHistory(ctx, agentScore)
	if err == nil {
		results = append(results, historyResult)
		totalDelta += historyResult.Delta
	}

	// Factor 3: Time of Day (15%)
	timeResult := s.evaluateTimeOfDay(agentScore)
	results = append(results, timeResult)
	totalDelta += timeResult.Delta

	// Factor 4: Anomaly (20%) - placeholder for Phase 3
	anomalyResult := s.evaluateAnomaly(actionCtx, agentScore)
	results = append(results, anomalyResult)
	totalDelta += anomalyResult.Delta

	// Factor 5: Tool Frequency (20%) - placeholder for Phase 3
	freqResult := s.evaluateFrequency(actionCtx, agentScore)
	results = append(results, freqResult)
	totalDelta += freqResult.Delta

	newScore := clamp(agentScore.Score+totalDelta, 0, 100)

	breakdown := FactorBreakdown{
		Identity:  identityResult.Score,
		History:   historyResult.Score,
		Time:      timeResult.Score,
		Anomaly:   anomalyResult.Score,
		Frequency: freqResult.Score,
	}

	return newScore, breakdown, results, nil
}

func (s *Scorer) evaluateIdentity(score *AgentScore) FactorResult {
	if score.IdentityVerified {
		return FactorResult{
			Factor: FactorIdentity,
			Score:  100,
			Delta:  0,
			Reason: "SPIFFE identity verified",
		}
	}
	if score.SPIFFEID == "" {
		return FactorResult{
			Factor: FactorIdentity,
			Score:  50,
			Delta:  0,
			Reason: "No SPIFFE ID present",
		}
	}
	return FactorResult{
		Factor: FactorIdentity,
		Score:  30,
		Delta:  -10,
		Reason: "SPIFFE ID present but not verified",
	}
}

func (s *Scorer) evaluateHistory(ctx context.Context, score *AgentScore) (FactorResult, error) {
	history, err := s.store.GetHistory(ctx, score.AgentID, 100)
	if err != nil || len(history) == 0 {
		return FactorResult{
			Factor: FactorHistory,
			Score:  70,
			Delta:  0,
			Reason: "No history yet",
		}, err
	}

	denyCount := 0
	for _, h := range history {
		if h.NewScore < h.PreviousScore {
			denyCount++
		}
	}
	denyRatio := float64(denyCount) / float64(len(history))

	if denyRatio > 0.5 {
		return FactorResult{
			Factor: FactorHistory,
			Score:  25,
			Delta:  -25,
			Reason: "High denial ratio",
		}, nil
	}
	if denyRatio > 0.2 {
		return FactorResult{
			Factor: FactorHistory,
			Score:  55,
			Delta:  -15,
			Reason: "Moderate denial ratio",
		}, nil
	}
	return FactorResult{
		Factor: FactorHistory,
		Score:  85,
		Delta:  5,
		Reason: "Good behavioral history",
	}, nil
}

func (s *Scorer) evaluateTimeOfDay(score *AgentScore) FactorResult {
	hour := time.Now().Hour()
	// Typical business hours: 9am-6pm
	if hour >= 9 && hour <= 18 {
		return FactorResult{
			Factor: FactorTimeOfDay,
			Score:  100,
			Delta:  5,
			Reason: "Access during business hours",
		}
	}
	return FactorResult{
		Factor: FactorTimeOfDay,
		Score:  60,
		Delta:  -10,
		Reason: "Access outside business hours",
	}
}

func (s *Scorer) evaluateAnomaly(ctx map[string]interface{}, score *AgentScore) FactorResult {
	// Phase 3 will implement full anomaly detection
	return FactorResult{
		Factor: FactorAnomaly,
		Score:  70,
		Delta:  0,
		Reason: "No anomalies detected (Phase 2 placeholder)",
	}
}

func (s *Scorer) evaluateFrequency(ctx map[string]interface{}, score *AgentScore) FactorResult {
	// Phase 3 will implement frequency analysis
	return FactorResult{
		Factor: FactorFrequency,
		Score:  70,
		Delta:  0,
		Reason: "Normal tool usage (Phase 2 placeholder)",
	}
}

func clamp(val, min, max int) int {
	return int(math.Max(float64(min), math.Min(float64(max), float64(val))))
}