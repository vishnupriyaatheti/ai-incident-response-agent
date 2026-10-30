package com.incident.monitoring_service;

import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/monitoring")
public class MonitoringController {

    @GetMapping("/services/{serviceName}/health")
    public Map<String, Object> getServiceHealth(
            @PathVariable String serviceName) {

        return Map.of(
                "service", serviceName,
                "status", "DEGRADED",
                "response_time_ms", 1800,
                "error_rate", 18
        );
    }

    @GetMapping("/services/{serviceName}/logs")
    public Map<String, Object> getRecentLogs(
            @PathVariable String serviceName,
            @RequestParam(defaultValue = "30") int minutes) {

        List<Map<String, String>> logs = List.of(
                Map.of(
                        "timestamp", "2026-10-28T09:42:10",
                        "level", "INFO",
                        "message", "payment-service version 2.4.1 started"
                ),
                Map.of(
                        "timestamp", "2026-10-28T09:45:03",
                        "level", "ERROR",
                        "message", "Database connection timeout"
                ),
                Map.of(
                        "timestamp", "2026-10-28T09:45:05",
                        "level", "ERROR",
                        "message", "POST /payments returned HTTP 500"
                ),
                Map.of(
                        "timestamp", "2026-10-28T09:46:12",
                        "level", "ERROR",
                        "message", "Connection pool acquisition timeout"
                )
        );

        return Map.of(
                "service", serviceName,
                "minutes", minutes,
                "logs", logs
        );
    }

    @GetMapping("/services/{serviceName}/database")
    public Map<String, Object> getDatabaseHealth(
            @PathVariable String serviceName) {

        return Map.of(
                "service", serviceName,
                "database", Map.of(
                        "status", "HEALTHY",
                        "total_connections", 28,
                        "active_queries", 8,
                        "max_connections", 50,
                        "average_query_ms", 12
                )
        );
    }

    @GetMapping("/services/{serviceName}/deployments")
    public Map<String, Object> getRecentDeployments(
            @PathVariable String serviceName) {

        return Map.of(
                "service", serviceName,
                "deployment", Map.of(
                        "version", "2.4.1",
                        "deployed_minutes_ago", 15,
                        "previous_version", "2.4.0"
                )
        );
    }

    @GetMapping("/services/{serviceName}/connection-pool")
    public Map<String, Object> getConnectionPoolStatus(
            @PathVariable String serviceName) {

        return Map.of(
                "service", serviceName,
                "connection_pool", Map.of(
                        "max_pool_size", 20,
                        "active_connections", 20,
                        "idle_connections", 0,
                        "waiting_requests", 14,
                        "acquisition_timeout_ms", 3000
                )
        );
    }
}