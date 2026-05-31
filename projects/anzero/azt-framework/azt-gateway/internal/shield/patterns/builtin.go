package patterns

type ThreatPattern struct {
    Name     string
    Patterns []string
    Severity int
}

var PromptInjectionPatterns = []ThreatPattern{
    {
        Name: "instruction_override",
        Patterns: []string{
            "(?i)ignore.{0,20}(previous|all|your).{0,20}(instruction|command|rule)",
            "(?i)forget.{0,20}(everything|all|previous|you were)",
            "(?i)you are now (a |the )",
            "(?i)new instructions?:",
            "(?i)<\\|im_start\\|>.*<\\|im_end\\|>",
            "(?i)\\[INST\\].*\\[/INST\\]",
        },
        Severity: 80,
    },
    {
        Name: "role_playing_jailbreak",
        Patterns: []string{
            "(?i)pretend you are (not? )?[a-zA-Z]+",
            "(?i)roleplay as (a |an )",
            "(?i)you can (now )?ignore",
            "(?i) DAN[, ]",
        },
        Severity: 60,
    },
    {
        Name: "context_escape",
        Patterns: []string{
            "(?i)\\{.*\\}.*\\{.*\\}",
            "(?i)```json\\s*\\{",
            "(?i)<script.*>.*</script>",
            "(?i)\\[TOOL_CALL\\]",
        },
        Severity: 40,
    },
}