package grpc

import (
    "context"
    "fmt"
    "net"

    "github.com/anzero/azt-framework/azt-gateway/internal/audit"
    "github.com/anzero/azt-framework/azt-gateway/internal/policy"
    "github.com/anzero/azt-framework/azt-gateway/internal/shield"
    "github.com/anzero/azt-framework/azt-gateway/internal/trust"
    v1 "github.com/anzero/azt-framework/proto/azt/v1"
    "go.uber.org/zap"
    "google.golang.org/grpc"
    "google.golang.org/grpc/codes"
    "google.golang.org/grpc/reflection"
    "google.golang.org/grpc/status"
)

// StoreReader defines the interface for reading and writing trust scores
type StoreReader interface {
    GetScore(ctx context.Context, agentID string) (*trust.AgentScore, error)
    UpsertScore(ctx context.Context, agentID string, score int, identityVerified bool, spiffeID string) error
    AddHistory(ctx context.Context, agentID string, prevScore, newScore, delta int, factor, reason string, actionCtx map[string]interface{}) error
}

// Scorer defines the interface for evaluating trust factors
type Scorer interface {
    EvaluateAllFactors(ctx context.Context, agentID string, actionCtx map[string]interface{}) (int, trust.FactorBreakdown, []trust.FactorResult, error)
}

type Server struct {
    addr   string
    logger *zap.Logger
    engine *policy.Engine
    audit  *audit.Logger
    scorer Scorer
    store  StoreReader
    shield *shield.Shield
    v1.UnimplementedAZTGatewayServer
}

func NewServer(addr string, logger *zap.Logger, engine *policy.Engine, auditLogger *audit.Logger, scorer Scorer, store StoreReader, shield *shield.Shield) *Server {
    return &Server{
        addr:   addr,
        logger: logger,
        engine: engine,
        audit:  auditLogger,
        scorer: scorer,
        store:  store,
        shield: shield,
    }
}

func (s *Server) Enforce(ctx context.Context, req *v1.EnforcementRequest) (*v1.EnforcementResponse, error) {
    s.logger.Info("Enforce request received",
        zap.String("agent_id", req.Context.AgentId),
        zap.String("action", req.Context.Action),
        zap.String("tool", req.Context.Tool),
    )

    // Get trust score from store
    agentScore, err := s.store.GetScore(ctx, req.Context.AgentId)
    if err != nil {
        s.logger.Warn("Failed to get trust score", zap.Error(err))
    }
    req.Context.TrustScore = int32(agentScore.Score)

    decision, reason := s.engine.Evaluate(req.Context)

    s.audit.LogEnforcement(audit.AuditEvent{
        AgentId:    req.Context.AgentId,
        Action:     req.Context.Action,
        Tool:       req.Context.Tool,
        Decision:   decision.String(),
        Reason:     reason,
        TrustScore: agentScore.Score,
        SessionId:  req.Context.SessionId,
    })

    return &v1.EnforcementResponse{
        Decision:          decision,
        Reason:            reason,
        UpdatedTrustScore: int32(agentScore.Score),
    }, nil
}

func (s *Server) GetTrustScore(ctx context.Context, req *v1.TrustScoreRequest) (*v1.TrustScoreResponse, error) {
    agentScore, err := s.store.GetScore(ctx, req.AgentId)
    if err != nil {
        return nil, err
    }
    return &v1.TrustScoreResponse{
        Score:   int32(agentScore.Score),
        Reason:  "Current trust score",
        AgentId: agentScore.AgentID,
    }, nil
}

func (s *Server) UpdateTrustScore(ctx context.Context, req *v1.UpdateTrustScoreRequest) (*v1.TrustScoreResponse, error) {
    agentScore, err := s.store.GetScore(ctx, req.AgentId)
    if err != nil {
        agentScore = &trust.AgentScore{AgentID: req.AgentId, Score: 70}
    }

    // Convert map[string]string to map[string]interface{}
    actionCtx := make(map[string]interface{}, len(req.ActionContext))
    for k, v := range req.ActionContext {
        actionCtx[k] = v
    }

    newScore, breakdown, _, err := s.scorer.EvaluateAllFactors(ctx, req.AgentId, actionCtx)
    if err != nil {
        return nil, err
    }

    // Persist
    s.store.UpsertScore(ctx, req.AgentId, newScore, false, "")

    // Log history
    delta := newScore - agentScore.Score
    s.store.AddHistory(ctx, req.AgentId, agentScore.Score, newScore, delta, req.Factor, req.Reason, actionCtx)

    return &v1.TrustScoreResponse{
        Score:    int32(newScore),
        Reason:   req.Reason,
        Breakdown: &v1.FactorBreakdown{
            Identity:  int32(breakdown.Identity),
            History:   int32(breakdown.History),
            Time:      int32(breakdown.Time),
            Anomaly:   int32(breakdown.Anomaly),
            Frequency: int32(breakdown.Frequency),
        },
        AgentId: req.AgentId,
    }, nil
}

func (s *Server) GetAgentScore(ctx context.Context, req *v1.GetAgentScoreRequest) (*v1.TrustScoreResponse, error) {
    return s.UpdateTrustScore(ctx, &v1.UpdateTrustScoreRequest{
        AgentId: req.AgentId,
    })
}

func (s *Server) ThreatShieldScan(ctx context.Context, req *v1.ThreatShieldRequest) (*v1.ThreatShieldResponse, error) {
    s.logger.Info("ThreatShieldScan request received",
        zap.String("agent_id", req.AgentId),
        zap.String("action", req.Action),
        zap.String("tool", req.Tool),
    )

    input := &shield.ShieldInput{
        AgentID:    req.AgentId,
        Action:     req.Action,
        Tool:       req.Tool,
        Prompt:     req.Prompt,
        Output:     req.Output,
        TrustScore: int(req.TrustScore),
        Timestamp:  req.Timestamp,
    }

    decision, err := s.shield.Evaluate(ctx, input)
    if err != nil {
        return nil, status.Errorf(codes.Internal, "shield evaluation failed: %v", err)
    }

    return &v1.ThreatShieldResponse{
        Decision:      decision.Action,
        SeverityScore: int32(decision.SeverityScore),
        Indicators:    decision.Indicators,
        Reason:       decision.Reason,
    }, nil
}

func (s *Server) Start() error {
    lis, err := net.Listen("tcp", s.addr)
    if err != nil {
        return fmt.Errorf("failed to listen: %w", err)
    }
    grpcServer := grpc.NewServer()
    v1.RegisterAZTGatewayServer(grpcServer, s)
    reflection.Register(grpcServer)
    s.logger.Info("gRPC server listening", zap.String("addr", s.addr))
    return grpcServer.Serve(lis)
}