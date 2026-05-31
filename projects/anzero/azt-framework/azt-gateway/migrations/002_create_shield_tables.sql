CREATE TABLE IF NOT EXISTS threat_patterns (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    pattern TEXT NOT NULL,
    pattern_type VARCHAR(20) NOT NULL,
    severity INTEGER NOT NULL CHECK (severity >= 0 AND severity <= 100),
    source VARCHAR(50) NOT NULL DEFAULT 'builtin',
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS threat_detections (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(255) NOT NULL,
    analyzer VARCHAR(50) NOT NULL,
    pattern_matched VARCHAR(100),
    severity INTEGER NOT NULL,
    indicators JSONB,
    context JSONB,
    action_taken VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_threat_detections_agent_id ON threat_detections(agent_id);
CREATE INDEX IF NOT EXISTS idx_threat_detections_created_at ON threat_detections(created_at);
CREATE INDEX IF NOT EXISTS idx_threat_patterns_category ON threat_patterns(category);
