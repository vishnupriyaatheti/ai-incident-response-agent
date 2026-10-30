from mcp_client import call_mcp_tool_sync
import requests

BASE_URL = "http://localhost:8080/api/monitoring/services"

def get_service_health(service_name):
    return call_mcp_tool_sync(
        "get_service_health",
        {
            "service_name": service_name
        }
    )


def get_recent_logs(service_name, minutes=30):
    response = requests.get(
        f"{BASE_URL}/{service_name}/logs",
        params={"minutes": minutes},
        timeout=5
    )

    response.raise_for_status()
    return response.json()


def check_database_health(service_name):
    response = requests.get(
        f"{BASE_URL}/{service_name}/database",
        timeout=5
    )

    response.raise_for_status()
    return response.json()


def get_recent_deployments(service_name):
    response = requests.get(
        f"{BASE_URL}/{service_name}/deployments",
        timeout=5
    )

    response.raise_for_status()
    return response.json()


def get_connection_pool_status(service_name):
    return call_mcp_tool_sync(
        "get_connection_pool_status",
        {
            "service_name": service_name
        }
    )

def rollback_deployment(service_name):
    return {
        "service": service_name,
        "action": "rollback",
        "from_version": "2.4.1",
        "to_version": "2.4.0",
        "status": "SUCCESS"
    }