package main

import (
    "context"
    "flag"
    "fmt"
    "os"

    "github.com/anzero/azt-framework/azt-gateway/internal/audit"
    "github.com/anzero/azt-framework/azt-gateway/internal/grpc"
    "github.com/anzero/azt-framework/azt-gateway/internal/policy"
    "github.com/anzero/azt-framework/azt-gateway/internal/trust"
    "github.com/jackc/pgx/v5/pgxpool"
    "go.uber.org/zap"
    "go.uber.org/zap/zapcore"
)

func main() {
    addr := flag.String("addr", "localhost:50051", "gRPC server address")
    dbURL := flag.String("db-url", "postgres://localhost:5432/azt?sslmode=disable", "PostgreSQL connection URL")
    flag.Parse()

    config := zap.NewProductionConfig()
    config.EncoderConfig.TimeKey = "timestamp"
    config.EncoderConfig.EncodeTime = zapcore.ISO8601TimeEncoder
    logger, _ := config.Build()

    // Initialize PostgreSQL connection pool
    pool, err := pgxpool.New(context.Background(), *dbURL)
    if err != nil {
        logger.Fatal("Failed to create connection pool", zap.Error(err))
    }
    defer pool.Close()

    // Run migrations
    store := trust.NewStore(pool)
    if err := store.InitSchema(context.Background()); err != nil {
        logger.Fatal("Failed to initialize schema", zap.Error(err))
    }

    // Initialize services
    engine := policy.NewEngine()
    auditLogger := audit.NewLogger(logger)
    scorer := trust.NewScorer(store)

    // Load policies if path provided
    if policyPath := os.Getenv("AZT_POLICY_PATH"); policyPath != "" {
        if err := engine.LoadPolicy(policyPath, "default"); err != nil {
            logger.Warn("Failed to load policy", zap.Error(err))
        }
    }

    server := grpc.NewServer(*addr, logger, engine, auditLogger, scorer, store)
    logger.Info(fmt.Sprintf("Starting AZT Gateway on %s", *addr))
    if err := server.Start(); err != nil {
        logger.Fatal("Failed to start server", zap.Error(err))
    }
}