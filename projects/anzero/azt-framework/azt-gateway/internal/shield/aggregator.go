package shield

type Aggregator struct {
    blockThreshold int
    alertThreshold int
}

func NewAggregator(blockThreshold, alertThreshold int) *Aggregator {
    return &Aggregator{
        blockThreshold: blockThreshold,
        alertThreshold: alertThreshold,
    }
}

func (a *Aggregator) Aggregate(results []*AnalyzerResult) (int, string) {
    if len(results) == 0 {
        return 0, "ALLOW"
    }

    maxScore := 0
    for _, r := range results {
        if r.Score > maxScore {
            maxScore = r.Score
        }
    }

    var action string
    if maxScore >= a.blockThreshold {
        action = "BLOCK"
    } else if maxScore >= a.alertThreshold {
        action = "LOG_ALERT"
    } else {
        action = "ALLOW"
    }

    return maxScore, action
}