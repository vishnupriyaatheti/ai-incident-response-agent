services = {
    "payment-service": {
    "status": "DEGRADED",
    "response_time_ms": 1800,
    "error_rate": 18,

    "logs": [
        {
            "timestamp": "2026-10-28T09:42:10",
            "level": "INFO",
            "message": "payment-service version 2.4.1 started"
        },
        {
            "timestamp": "2026-10-28T09:45:03",
            "level": "ERROR",
            "message": "Database connection timeout"
        },
        {
            "timestamp": "2026-10-28T09:45:05",
            "level": "ERROR",
            "message": "POST /payments returned HTTP 500"
        },
        {
            "timestamp": "2026-10-28T09:46:12",
            "level": "ERROR",
            "message": "Connection pool acquisition timeout"
        }
    ],

    "database": {
        "status": "HEALTHY",
        "active_connections": 8,
        "max_connections": 50,
        "average_query_ms": 12
    },

    "recent_deployment": {
        "version": "2.4.1",
        "deployed_minutes_ago": 15,
        "previous_version": "2.4.0"
    }
},

    "order-service": {
        "status": "HEALTHY",
        "response_time_ms": 320,
        "error_rate": 1,
        "logs": [
            "INFO Order created successfully"
        ],
        "database_status": "HEALTHY",
        "recent_deployment": None
    },

    "inventory-service": {
        "status": "HEALTHY",
        "response_time_ms": 240,
        "error_rate": 0,
        "logs": [
            "INFO Inventory lookup completed"
        ],
        "database_status": "HEALTHY",
        "recent_deployment": None
    },

    "notification-service": {
        "status": "DEGRADED",
        "response_time_ms": 2500,
        "error_rate": 6,
        "logs": [
            "WARN Message queue backlog detected"
        ],
        "database_status": "HEALTHY",
        "recent_deployment": None
    }
}