package policy

import (
	"fmt"
	"strings"

	v1 "github.com/anzero/azt-framework/proto/azt/v1"
)

type Engine struct {
	policies map[string]*Policy
}

func NewEngine() *Engine {
	return &Engine{policies: make(map[string]*Policy)}
}

func (e *Engine) LoadPolicy(path string, agentId string) error {
	policy, err := LoadPolicy(path)
	if err != nil {
		return err
	}
	e.policies[agentId] = policy
	return nil
}

func (e *Engine) Evaluate(ctx *v1.ActionContext) (v1.Decision, string) {
	policy, ok := e.policies[ctx.AgentId]
	if !ok {
		return v1.Decision_DECISION_ALLOW, "No policy found, allowing by default"
	}

	for _, rule := range policy.Rules {
		if e.ruleMatches(rule, ctx) {
			if rule.Effect == "allow" {
				return v1.Decision_DECISION_ALLOW, fmt.Sprintf("Allowed by rule: %s", rule.Name)
			}
			if rule.Effect == "deny" {
				return v1.Decision_DECISION_DENY, fmt.Sprintf("Denied by rule: %s", rule.Name)
			}
		}
	}

	return v1.Decision_DECISION_ALLOW, "No matching rule, allowing by default"
}

func (e *Engine) ruleMatches(rule Rule, ctx *v1.ActionContext) bool {
	if len(rule.Tools) > 0 {
		matched := false
		for _, tool := range rule.Tools {
			if strings.EqualFold(tool, ctx.Tool) {
				matched = true
				break
			}
		}
		if !matched {
			return false
		}
	}

	if len(rule.Actions) > 0 {
		matched := false
		for _, action := range rule.Actions {
			if strings.EqualFold(action, ctx.Action) {
				matched = true
				break
			}
		}
		if !matched {
			return false
		}
	}

	for _, cond := range rule.Conditions {
		if cond.TrustScoreBelow != nil && ctx.TrustScore >= int32(*cond.TrustScoreBelow) {
			return false
		}
		if cond.RiskLevel != nil {
			// Phase 1: RiskLevel conditions are not yet implemented.
			// The proto ActionContext doesn't have a risk_level field.
			// Skip this condition for now; proper support requires adding
			// risk_level to the proto and regenerating.
		}
	}

	return true
}