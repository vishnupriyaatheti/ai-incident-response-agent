# from tools import (
#     get_service_health,
#     get_recent_logs,
#     check_database_health,
#     get_recent_deployments
# )


# service_name = "payment-service"

# print("HEALTH:")
# print(get_service_health(service_name))

# print("\nLOGS:")
# print(get_recent_logs(service_name))

# print("\nDATABASE:")
# print(check_database_health(service_name))

# print("\nDEPLOYMENT:")
# print(get_recent_deployments(service_name))

from agent import investigate_incident


incident = """
Investigate why payment-service is returning HTTP 500 errors.
"""

print("INCIDENT:")
print(incident)

result = investigate_incident(incident)

print("\nFINAL DIAGNOSIS:")
print(result)