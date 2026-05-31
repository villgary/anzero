package api

import (
	"github.com/gin-gonic/gin"
)

func NewRouter() *gin.Engine {
	r := gin.Default()

	// CORS middleware
	r.Use(func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}
		c.Next()
	})

	// Health check
	r.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok"})
	})

	// API v1 routes
	v1 := r.Group("/api/v1")
	{
		v1.GET("/dashboard/stats", func(c *gin.Context) {
			c.JSON(200, gin.H{
				"activeAgents":     24,
				"threatsBlocked":   12,
				"avgTrustScore":    78,
				"pendingApprovals": 3,
			})
		})

		v1.GET("/alerts", func(c *gin.Context) {
			c.JSON(200, gin.H{
				"alerts": []gin.H{
					{"id": "1", "severity": "critical", "message": "Prompt injection attempt", "agentId": "agent-42"},
					{"id": "2", "severity": "high", "message": "Unusual tool sequence", "agentId": "agent-17"},
				},
			})
		})

		v1.GET("/agents", func(c *gin.Context) {
			c.JSON(200, gin.H{
				"agents": []gin.H{
					{"id": "agent-42", "name": "Email Agent", "trustScore": 72, "status": "active"},
					{"id": "agent-17", "name": "Search Agent", "trustScore": 85, "status": "active"},
					{"id": "agent-99", "name": "Data Agent", "trustScore": 45, "status": "inactive"},
				},
			})
		})

		v1.GET("/agents/:id", func(c *gin.Context) {
			id := c.Param("id")
			c.JSON(200, gin.H{
				"id":           id,
				"name":         "Email Agent",
				"trustScore":   72,
				"status":       "active",
				"lastActivity": "2024-01-15T10:30:00Z",
			})
		})

		v1.GET("/approvals", func(c *gin.Context) {
			c.JSON(200, gin.H{
				"approvals": []gin.H{
					{"id": "1", "agentId": "agent-99", "action": "tool_call", "tool": "delete_database", "reason": "Database cleanup", "status": "pending"},
				},
			})
		})
	}

	return r
}