-- 001_create_trust_tables.sql
CREATE TABLE IF NOT EXISTS agent_scores (
    agent_id VARCHAR(255) PRIMARY KEY,
    score INTEGER NOT NULL DEFAULT 70 CHECK (score >= 0 AND score <= 100),
    identity_verified BOOLEAN DEFAULT FALSE,
    spiffe_id VARCHAR(512),
    last_action_at TIMESTAMP,
    last_updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS score_history (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(255) NOT NULL REFERENCES agent_scores(agent_id) ON DELETE CASCADE,
    previous_score INTEGER NOT NULL,
    new_score INTEGER NOT NULL,
    delta INTEGER NOT NULL,
    factor VARCHAR(50) NOT NULL,
    reason TEXT,
    action_context JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_score_history_agent_id ON score_history(agent_id);
CREATE INDEX IF NOT EXISTS idx_score_history_created_at ON score_history(created_at);
