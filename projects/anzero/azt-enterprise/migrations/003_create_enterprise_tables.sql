-- Users for Web UI authentication
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'viewer',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- API keys for SDK authentication
CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    key_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    user_id INTEGER REFERENCES users(id),
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);

-- Approval requests
CREATE TABLE IF NOT EXISTS approval_requests (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(255) NOT NULL,
    action VARCHAR(100) NOT NULL,
    tool VARCHAR(100),
    parameters JSONB,
    reason TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    requested_by VARCHAR(255) NOT NULL,
    requested_at TIMESTAMP DEFAULT NOW(),
    resolved_by VARCHAR(255),
    resolved_at TIMESTAMP,
    comment TEXT
);

-- Report schedules
CREATE TABLE IF NOT EXISTS report_schedules (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    report_type VARCHAR(50) NOT NULL,
    frequency VARCHAR(20) NOT NULL,
    recipients TEXT[],
    enabled BOOLEAN DEFAULT TRUE,
    last_run_at TIMESTAMP,
    next_run_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_approval_requests_status ON approval_requests(status);
CREATE INDEX IF NOT EXISTS idx_approval_requests_agent_id ON approval_requests(agent_id);