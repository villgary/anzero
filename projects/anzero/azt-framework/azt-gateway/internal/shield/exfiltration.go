package shield

import (
    "context"
    "regexp"
)

type ExfiltrationAnalyzer struct {
    compiledPatterns []*compiledPattern
}

func NewExfiltrationAnalyzer(additionalPatterns []string) *ExfiltrationAnalyzer {
    ea := &ExfiltrationAnalyzer{
        compiledPatterns: []*compiledPattern{
            // Credential patterns
            {regex: regexp.MustCompile("(?i)(api[_-]?key|token|secret|password|passwd|pwd)['\"]?\\s*[:=]\\s*['\"]?[a-zA-Z0-9]{16,}['\"]?"), name: "credential_pattern", severity: 90},
            {regex: regexp.MustCompile("(?i)Bearer\\s+[a-zA-Z0-9\\-_]+\\.[a-zA-Z0-9\\-_]+\\.[a-zA-Z0-9\\-_]+"), name: "bearer_token", severity: 90},
            {regex: regexp.MustCompile("(?i)sk-[a-zA-Z0-9]{32,}"), name: "openai_key", severity: 90},
            {regex: regexp.MustCompile("(?i)ghp_[a-zA-Z0-9]{36,}"), name: "github_token", severity: 90},
            // PII patterns
            {regex: regexp.MustCompile("\\b\\d{3}-\\d{2}-\\d{4}\\b"), name: "ssn", severity: 70},
            {regex: regexp.MustCompile("\\b\\d{16}\\b"), name: "credit_card", severity: 85},
        },
    }
    return ea
}

func (e *ExfiltrationAnalyzer) Name() string {
    return "data_exfiltration"
}

func (e *ExfiltrationAnalyzer) Analyze(ctx context.Context, input *ShieldInput) (*AnalyzerResult, error) {
    result := &AnalyzerResult{
        Analyzer:   e.Name(),
        Score:      0,
        Indicators: []string{},
    }

    textToCheck := input.Output
    if textToCheck == "" {
        textToCheck = input.Prompt
    }

    maxSeverity := 0
    for _, cp := range e.compiledPatterns {
        if cp.regex.MatchString(textToCheck) {
            result.Indicators = append(result.Indicators, cp.name)
            if cp.severity > maxSeverity {
                maxSeverity = cp.severity
            }
        }
    }

    result.Score = maxSeverity
    return result, nil
}