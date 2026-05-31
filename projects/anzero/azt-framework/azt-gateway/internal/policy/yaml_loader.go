package policy

import (
	"fmt"
	"os"

	"gopkg.in/yaml.v3"
)

type Policy struct {
	Agent   string  `yaml:"agent"`
	Version int     `yaml:"version"`
	Rules   []Rule  `yaml:"rules"`
}

type Rule struct {
	Name       string      `yaml:"name"`
	Effect     string      `yaml:"effect"`
	Tools      []string    `yaml:"tools,omitempty"`
	Actions    []string    `yaml:"actions,omitempty"`
	Conditions []Condition `yaml:"conditions,omitempty"`
}

type Condition struct {
	TrustScoreBelow *int    `yaml:"trust_score_below,omitempty"`
	RiskLevel       *string `yaml:"risk_level,omitempty"`
}

func LoadPolicy(path string) (*Policy, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("failed to read policy file: %w", err)
	}
	var policy Policy
	if err := yaml.Unmarshal(data, &policy); err != nil {
		return nil, fmt.Errorf("failed to parse YAML: %w", err)
	}
	return &policy, nil
}