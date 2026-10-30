import requests
from mcp.server import MCPServer


mcp = MCPServer("incident-monitoring-tools")

BASE_URL = "http://localhost:8080/api/monitoring/services"


@mcp.tool()
def get_service_health(service_name: str) -> dict:
    """Get current health information for a microservice."""

    response = requests.get(
        f"{BASE_URL}/{service_name}/health",
        timeout=5
    )

    response.raise_for_status()
    return response.json()


@mcp.tool()
def get_connection_pool_status(service_name: str) -> dict:
    """Inspect the application's database connection pool."""

    response = requests.get(
        f"{BASE_URL}/{service_name}/connection-pool",
        timeout=5
    )

    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    mcp.run()