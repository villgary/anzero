package main

import (
	"log"
	"os"

	"github.com/anzero/azt-enterprise/api-server/internal/api"
)

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	router := api.NewRouter()
	log.Printf("Starting API server on :%s", port)
	if err := router.Run(":" + port); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}