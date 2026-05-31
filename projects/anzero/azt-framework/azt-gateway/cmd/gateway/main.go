package main

import (
	"flag"
	"fmt"

	"github.com/anzero/azt-framework/azt-gateway/internal/grpc"
	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
)

func main() {
	addr := flag.String("addr", "localhost:50051", "gRPC server address")
	flag.Parse()

	config := zap.NewProductionConfig()
	config.EncoderConfig.TimeKey = "timestamp"
	config.EncoderConfig.EncodeTime = zapcore.ISO8601TimeEncoder
	logger, _ := config.Build()

	server := grpc.NewServer(*addr, logger)
	logger.Info(fmt.Sprintf("Starting AZT Gateway on %s", *addr))
	if err := server.Start(); err != nil {
		logger.Fatal("Failed to start server", zap.Error(err))
	}
}
