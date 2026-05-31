package shield

import (
    "context"
    "regexp"

    "github.com/anzero/azt-framework/azt-gateway/internal/shield/patterns"
)

type compiledPattern struct {
    regex    *regexp.Regexp
    name     string
    severity int
}

type InjectorAnalyzer struct {
    compiledPatterns []*compiledPattern
}

func NewInjectorAnalyzer(additionalPatterns []string) *InjectorAnalyzer {
    ia := &InjectorAnalyzer{
        compiledPatterns: make([]*compiledPattern, 0),
    }
    for _, p := range patterns.PromptInjectionPatterns {
        for _, pattern := range p.Patterns {
            re := regexp.MustCompile(pattern)
            ia.compiledPatterns = append(ia.compiledPatterns, &compiledPattern{
                regex:    re,
                name:     p.Name,
                severity: p.Severity,
            })
        }
    }
    return ia
}

func (i *InjectorAnalyzer) Name() string {
    return "prompt_injection"
}

func (i *InjectorAnalyzer) Analyze(ctx context.Context, input *ShieldInput) (*AnalyzerResult, error) {
    result := &AnalyzerResult{
        Analyzer:   i.Name(),
        Score:      0,
        Indicators: []string{},
    }

    textToCheck := input.Prompt
    if textToCheck == "" {
        textToCheck = input.Output
    }

    maxSeverity := 0
    for _, cp := range i.compiledPatterns {
        if cp.regex.MatchString(textToCheck) {
            result.Indicators = append(result.Indicators, cp.name)
            if cp.severity > maxSeverity {
                maxSeverity = cp.severity
            }
        }
    }

    result.Score = maxSeverity
    if len(result.Indicators) > 0 && result.Score == 0 {
        result.Score = 30
    }

    return result, nil
}