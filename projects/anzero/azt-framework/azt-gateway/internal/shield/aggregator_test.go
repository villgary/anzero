package shield

import "testing"

func TestAggregator_BlockHighSeverity(t *testing.T) {
    agg := NewAggregator(80, 50)
    results := []*AnalyzerResult{
        {Analyzer: "injection", Score: 90, Indicators: []string{"ignore previous"}},
        {Analyzer: "exfil", Score: 20, Indicators: []string{}},
    }

    score, action := agg.Aggregate(results)
    if score < 80 {
        t.Errorf("Expected score >= 80, got %d", score)
    }
    if action != "BLOCK" {
        t.Errorf("Expected BLOCK, got %s", action)
    }
}

func TestAggregator_LogAlertMediumSeverity(t *testing.T) {
    agg := NewAggregator(80, 50)
    results := []*AnalyzerResult{
        {Analyzer: "injection", Score: 60, Indicators: []string{"suspicious pattern"}},
    }

    score, action := agg.Aggregate(results)
    if score < 50 || score >= 80 {
        t.Errorf("Expected score 50-79, got %d", score)
    }
    if action != "LOG_ALERT" {
        t.Errorf("Expected LOG_ALERT, got %s", action)
    }
}

func TestAggregator_AllowLowSeverity(t *testing.T) {
    agg := NewAggregator(80, 50)
    results := []*AnalyzerResult{
        {Analyzer: "injection", Score: 10, Indicators: []string{}},
        {Analyzer: "exfil", Score: 5, Indicators: []string{}},
    }

    score, action := agg.Aggregate(results)
    if score >= 50 {
        t.Errorf("Expected score < 50, got %d", score)
    }
    if action != "ALLOW" {
        t.Errorf("Expected ALLOW, got %s", action)
    }
}

func TestAggregator_EmptyResults(t *testing.T) {
    agg := NewAggregator(80, 50)
    score, action := agg.Aggregate([]*AnalyzerResult{})

    if score != 0 {
        t.Errorf("Expected 0 for empty results, got %d", score)
    }
    if action != "ALLOW" {
        t.Errorf("Expected ALLOW, got %s", action)
    }
}