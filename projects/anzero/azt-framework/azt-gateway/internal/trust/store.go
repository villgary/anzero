// internal/trust/store.go
package trust

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

type AgentScore struct {
	AgentID          string
	Score            int
	IdentityVerified bool
	SPIFFEID         string
	LastActionAt     time.Time
	LastUpdatedAt    time.Time
}

type ScoreHistory struct {
	ID              int
	AgentID         string
	PreviousScore   int
	NewScore        int
	Delta           int
	Factor          string
	Reason          string
	ActionContext   map[string]interface{}
	CreatedAt       time.Time
}

type ActionContextJSON map[string]interface{}

type Store struct {
	pool *pgxpool.Pool
}

func NewStore(pool *pgxpool.Pool) *Store {
	return &Store{pool: pool}
}

func (s *Store) InitSchema(ctx context.Context) error {
	schema := `
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
	`
	_, err := s.pool.Exec(ctx, schema)
	return err
}

func (s *Store) GetScore(ctx context.Context, agentID string) (*AgentScore, error) {
	row := s.pool.QueryRow(ctx,
		"SELECT agent_id, score, identity_verified, COALESCE(spiffe_id, ''), last_action_at, last_updated_at FROM agent_scores WHERE agent_id = $1",
		agentID)
	var score AgentScore
	var lastAction, lastUpdated *time.Time
	err := row.Scan(&score.AgentID, &score.Score, &score.IdentityVerified, &score.SPIFFEID, &lastAction, &lastUpdated)
	if err == pgx.ErrNoRows {
		return &AgentScore{
			AgentID: agentID,
			Score:   70,
		}, nil
	}
	if err != nil {
		return nil, fmt.Errorf("failed to get score: %w", err)
	}
	if lastAction != nil {
		score.LastActionAt = *lastAction
	}
	if lastUpdated != nil {
		score.LastUpdatedAt = *lastUpdated
	}
	return &score, nil
}

func (s *Store) UpsertScore(ctx context.Context, agentID string, score int, identityVerified bool, spiffeID string) error {
	_, err := s.pool.Exec(ctx, `
		INSERT INTO agent_scores (agent_id, score, identity_verified, spiffe_id, last_action_at, last_updated_at)
		VALUES ($1, $2, $3, $4, NOW(), NOW())
		ON CONFLICT (agent_id) DO UPDATE SET
			score = EXCLUDED.score,
			identity_verified = EXCLUDED.identity_verified,
			spiffe_id = EXCLUDED.spiffe_id,
			last_action_at = NOW(),
			last_updated_at = NOW()
	`, agentID, score, identityVerified, spiffeID)
	return err
}

func (s *Store) AddHistory(ctx context.Context, agentID string, prevScore, newScore, delta int, factor, reason string, actionCtx map[string]interface{}) error {
	ctxJSON, err := json.Marshal(actionCtx)
	if err != nil {
		return fmt.Errorf("failed to marshal action context: %w", err)
	}
	_, err = s.pool.Exec(ctx, `
		INSERT INTO score_history (agent_id, previous_score, new_score, delta, factor, reason, action_context)
		VALUES ($1, $2, $3, $4, $5, $6, $7)
	`, agentID, prevScore, newScore, delta, factor, reason, ctxJSON)
	return err
}

func (s *Store) GetHistory(ctx context.Context, agentID string, limit int) ([]ScoreHistory, error) {
	rows, err := s.pool.Query(ctx, `
		SELECT id, agent_id, previous_score, new_score, delta, factor, reason, action_context, created_at
		FROM score_history
		WHERE agent_id = $1
		ORDER BY created_at DESC
		LIMIT $2
	`, agentID, limit)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var history []ScoreHistory
	for rows.Next() {
		var h ScoreHistory
		var reasonNull *string
		var ctxJSON []byte
		var createdAt *time.Time
		err := rows.Scan(&h.ID, &h.AgentID, &h.PreviousScore, &h.NewScore, &h.Delta, &h.Factor, &reasonNull, &ctxJSON, &createdAt)
		if err != nil {
			return nil, err
		}
		if reasonNull != nil {
			h.Reason = *reasonNull
		}
		if ctxJSON != nil {
			json.Unmarshal(ctxJSON, &h.ActionContext)
		}
		if createdAt != nil {
			h.CreatedAt = *createdAt
		}
		history = append(history, h)
	}
	return history, nil
}
