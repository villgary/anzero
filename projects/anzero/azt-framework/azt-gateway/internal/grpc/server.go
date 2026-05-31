package grpc

import (
	"context"
	"fmt"
	"net"

	v1 "github.com/anzero/azt-framework/proto/azt/v1"
	"go.uber.org/zap"
	"google.golang.org/grpc"
	"google.golang.org/grpc/reflection"
)

type Server struct {
	addr   string
	logger *zap.Logger
	v1.UnimplementedAZTGatewayServer
}

func NewServer(addr string, logger *zap.Logger) *Server {
	return &Server{addr: addr, logger: logger}
}

func (s *Server) Enforce(ctx context.Context, req *v1.EnforcementRequest) (*v1.EnforcementResponse, error) {
	s.logger.Info("Enforce request received",
		zap.String("agent_id", req.Context.AgentId),
		zap.String("action", req.Context.Action),
		zap.String("tool", req.Context.Tool),
	)
	return &v1.EnforcementResponse{
		Decision:          v1.Decision_DECISION_ALLOW,
		Reason:            "Phase 1: Allow all (policy engine not yet connected)",
		UpdatedTrustScore: 70,
		RequestId:         fmt.Sprintf("req-%d", req.Context.Timestamp),
	}, nil
}

func (s *Server) GetTrustScore(ctx context.Context, req *v1.TrustScoreRequest) (*v1.TrustScoreResponse, error) {
	s.logger.Info("GetTrustScore request received",
		zap.String("agent_id", req.AgentId),
	)
	return &v1.TrustScoreResponse{
		Score:  70,
		Reason: "Phase 1: Default trust score",
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
