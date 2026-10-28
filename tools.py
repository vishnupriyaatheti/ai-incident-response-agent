from simulated_data import services


def get_service_health(service_name):
    service = services.get(service_name)

    if not service:
        return {
            "error": f"Unknown service: {service_name}"
        }

    return {
        "service": service_name,
        "status": service["status"],
        "response_time_ms": service["response_time_ms"],
        "error_rate": service["error_rate"]
    }


def get_recent_logs(service_name, minutes=30):
    service = services.get(service_name)

    if not service:
        return {
            "error": f"Unknown service: {service_name}"
        }

    return {
        "service": service_name,
        "minutes": minutes,
        "logs": service["logs"]
    }


def check_database_health(service_name):
    service = services.get(service_name)

    if not service:
        return {
            "error": f"Unknown service: {service_name}"
        }

    return {
        "service": service_name,
        "database": service["database"]
    }


def get_recent_deployments(service_name):
    service = services.get(service_name)

    if not service:
        return {
            "error": f"Unknown service: {service_name}"
        }

    return {
        "service": service_name,
        "deployment": service["recent_deployment"]
    }