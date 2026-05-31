package trust

import (
	"testing"
)

func TestClamp(t *testing.T) {
	tests := []struct {
		val, min, max int
		expected      int
	}{
		{50, 0, 100, 50},
		{-10, 0, 100, 0},
		{150, 0, 100, 100},
	}
	for _, tt := range tests {
		result := clamp(tt.val, tt.min, tt.max)
		if result != tt.expected {
			t.Errorf("clamp(%d, %d, %d) = %d; want %d", tt.val, tt.min, tt.max, result, tt.expected)
		}
	}
}

func TestFactorResult_Identity(t *testing.T) {
	scorer := &Scorer{}
	result := scorer.evaluateIdentity(&AgentScore{AgentID: "test", IdentityVerified: true})
	if result.Score != 100 {
		t.Errorf("expected verified identity score 100, got %d", result.Score)
	}
	if result.Delta != 0 {
		t.Errorf("expected delta 0, got %d", result.Delta)
	}
}

func TestFactorResult_IdentityUnverified(t *testing.T) {
	scorer := &Scorer{}
	result := scorer.evaluateIdentity(&AgentScore{AgentID: "test", IdentityVerified: false})
	if result.Score != 50 {
		t.Errorf("expected unverified identity score 50, got %d", result.Score)
	}
}

func TestFactorResult_TimeOfDay(t *testing.T) {
	scorer := &Scorer{}
	result := scorer.evaluateTimeOfDay(&AgentScore{})
	if result.Factor != FactorTimeOfDay {
		t.Errorf("expected factor %s, got %s", FactorTimeOfDay, result.Factor)
	}
}

func TestFactorResult_Anomaly(t *testing.T) {
	scorer := &Scorer{}
	result := scorer.evaluateAnomaly(map[string]interface{}{"tool": "read"}, &AgentScore{})
	if result.Factor != FactorAnomaly {
		t.Errorf("expected factor %s, got %s", FactorAnomaly, result.Factor)
	}
	if result.Score != 70 {
		t.Errorf("expected placeholder score 70, got %d", result.Score)
	}
}

func TestFactorResult_Frequency(t *testing.T) {
	scorer := &Scorer{}
	result := scorer.evaluateFrequency(map[string]interface{}{"tool": "read"}, &AgentScore{})
	if result.Factor != FactorFrequency {
		t.Errorf("expected factor %s, got %s", FactorFrequency, result.Factor)
	}
}