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


#version 2.4.1
# from agent import investigate_incident


# incident = """
# Investigate why payment-service is returning HTTP 500 errors.
# """

# print("INCIDENT:")
# print(incident)

# result = investigate_incident(incident)

# print("\nFINAL DIAGNOSIS:")
# print(result)

from graph import incident_graph

initial_state = {
    "incident": "Investigate why payment-service is returning HTTP 500 errors.",
    "service_name": "payment-service",
    "tools_used": [],
    "evidence": [],
    "suspected_cause": None,
    "recommended_action": None,
    "final_diagnosis": None,
    "iteration_count": 0,
    #"pending_tool_name": None,
    #"pending_tool_input": None,
    "pending_tool_calls": [],
    "messages": [],
    "approval_required": False,
    "approval_status": None,
    "action_executed": False,
}

result = incident_graph.invoke(initial_state)

print("\nTOOLS USED:")
print(result["tools_used"])

print("\nEVIDENCE COLLECTED:")
for item in result["evidence"]:
    print(item)

print("\nFINAL DIAGNOSIS:")
print(result["final_diagnosis"])

#print("\nFINAL STATE:")
#print(result)