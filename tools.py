import requests

BASE_URL = "http://localhost:8080/api/monitoring/services"

def get_service_health(service_name):
    response = requests.get(
        f"{BASE_URL}/{service_name}/health",
        timeout=5
    )

    response.raise_for_status()
    return response.json()


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
    response = requests.get(
        f"{BASE_URL}/{service_name}/connection-pool",
        timeout=5
    )

    response.raise_for_status()
    return response.json()