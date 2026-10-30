import json
from anthropic import Anthropic
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

from state import IncidentState
from tools import (
    get_connection_pool_status,
    get_service_health, 
    get_recent_logs,
    check_database_health,
    get_recent_deployments,
    rollback_deployment

)

load_dotenv()
client = Anthropic()
TOOLS = [
    {
        "name": "get_service_health",
        "description": "Get current health information for a microservice.",
        "input_schema": {
            "type": "object",
            "properties": {
                "service_name": {"type": "string"}
            },
            "required": ["service_name"]
        }
    },
    {
        "name": "get_recent_logs",
        "description": "Get recent logs for a microservice.",
        "input_schema": {
            "type": "object",
            "properties": {
                "service_name": {"type": "string"},
                "minutes": {"type": "integer"}
            },
            "required": ["service_name", "minutes"]
        }
    },
    {
        "name": "check_database_health",
        "description": "Check database health for a microservice.",
        "input_schema": {
            "type": "object",
            "properties": {
                "service_name": {"type": "string"}
            },
            "required": ["service_name"]
        }
    },
    {
        "name": "get_recent_deployments",
        "description": "Get recent deployment information for a microservice.",
        "input_schema": {
            "type": "object",
            "properties": {
                "service_name": {"type": "string"}
            },
            "required": ["service_name"]
        }
    },
    {
        "name": "get_connection_pool_status",
        "description": "Inspect the application's database connection pool. "
            "Use this when evidence suggests connection acquisition, "
            "pool exhaustion, or application-side database connectivity problems.",
        "input_schema": {
            "type": "object",
            "properties": {
                "service_name": {"type": "string"}
            },
            "required": ["service_name"]
        }
    }
]


SYSTEM_PROMPT = """
You are an incident-response investigation agent.

Use diagnostic tools to investigate the incident.

Rules:
- Gather evidence instead of guessing.
- Call more tools if evidence is incomplete.
- Do not invent system information.
- When enough evidence exists, provide:
  1. Likely root cause
  2. Supporting evidence
  3. Recommended next action
"""

def call_tool(name, tool_input):
    if name == "get_service_health":
        return get_service_health(**tool_input)

    if name == "get_recent_logs":
        return get_recent_logs(**tool_input)

    if name == "check_database_health":
        return check_database_health(**tool_input)

    if name == "get_recent_deployments":
        return get_recent_deployments(**tool_input)

    if name == "get_connection_pool_status":
        return get_connection_pool_status(**tool_input)

    raise ValueError(f"Unknown tool: {name}")

def initialize_incident(state: IncidentState):
    print("\n[Graph] Initializing incident")

    return {
        "tools_used": [],
        "evidence": [],
        "suspected_cause": None,
        "recommended_action": None,
        "final_diagnosis": None,
        "iteration_count": 0,
        #"pending_tool_name": None,
        #"pending_tool_input": None,
        "pending_tool_calls": [],
        "messages": [
            {
                "role": "user",
                "content": state["incident"]
            }
        ]
    }

def baseline_diagnostics_node(state: IncidentState):
    print("\n[Graph] Running baseline diagnostics")

    service_name = state["service_name"]

    baseline_calls = [
        {
            "name": "get_service_health",
            "input": {"service_name": service_name}
        },
        {
            "name": "get_recent_logs",
            "input": {
                "service_name": service_name,
                "minutes": 30
            }
        },
        {
            "name": "check_database_health",
            "input": {"service_name": service_name}
        },
        {
            "name": "get_recent_deployments",
            "input": {"service_name": service_name}
        }
    ]

    evidence = []
    tools_used = []

    for tool_call in baseline_calls:
        result = call_tool(
            tool_call["name"],
            tool_call["input"]
        )

        print(
            f"[Graph] {tool_call['name']} → {result}"
        )

        evidence.append({
            "tool": tool_call["name"],
            "input": tool_call["input"],
            "result": result
        })

        tools_used.append(tool_call["name"])

    evidence_summary = json.dumps(
        evidence,
        indent=2
    )

    messages = [
        {
            "role": "user",
            "content": (
                f"Investigate this incident:\n"
                f"{state['incident']}\n\n"
                f"Baseline diagnostic evidence:\n"
                f"{evidence_summary}\n\n"
                "Use targeted diagnostic tools only if additional "
                "evidence is needed."
            )
        }
    ]

    return {
        "tools_used": tools_used,
        "evidence": evidence,
        "messages": messages,
        "iteration_count": 0,
        "pending_tool_calls": []
    }

def agent_node(state: IncidentState):
    print("\n[Graph] Agent reasoning")

    response = client.messages.create(
        model="claude-haiku-5-5",
        max_tokens=1800,
        system=SYSTEM_PROMPT,
        tools=TOOLS,
        messages=state["messages"]
    )

    assistant_content = []
    tool_calls = []

    for block in response.content:

        if block.type == "text":
            assistant_content.append({
                "type": "text",
                "text": block.text
            })

        elif block.type == "tool_use":
            print(f"[Graph] Agent selected: {block.name}")

            tool_block = {
                "type": "tool_use",
                "id": block.id,
                "name": block.name,
                "input": block.input
            }

            # Store the exact tool_use block in message history
            assistant_content.append(tool_block)

            # Also store it for our LangGraph execution node
            tool_calls.append({
                "id": block.id,
                "name": block.name,
                "input": block.input
            })

    print(
        f"[Graph] Total tool calls requested: "
        f"{len(tool_calls)}"
    )

    updated_messages = state["messages"] + [
        {
            "role": "assistant",
            "content": assistant_content
        }
    ]

    if tool_calls:
        return {
            "messages": updated_messages,
            "pending_tool_calls": tool_calls
        }

    final_text = "\n".join(
        block["text"]
        for block in assistant_content
        if block["type"] == "text"
    )

    return {
        "messages": updated_messages,
        "final_diagnosis": final_text,
        "pending_tool_calls": []
    }


# def agent_node(state: IncidentState):
#     print("\n[Graph] Agent reasoning")

#     response = client.messages.create(
#         model="claude-haiku-5-5",
#         max_tokens=1200,
#         system=SYSTEM_PROMPT,
#         tools=TOOLS,
#         messages=state["messages"]
#     )

#     updated_messages = state["messages"] + [
#         {
#             "role": "assistant",
#             "content": response.content
#         }
#     ]
#     tool_calls = []
#     for block in response.content:
#         if block.type == "tool_use":
#             print(f"[Graph] Agent selected: {block.name}")

#             tool_calls.append({
#                 "id": block.id,
#                 "name": block.name,
#                 "input": block.input
#             })
#             print(
#         f"[Graph] Total tool calls requested: "
#         f"{len(tool_calls)}"
#     )


#             if tool_calls:
#                 return {
#                     "messages": updated_messages,
#                     "pending_tool_calls": tool_calls
#                 }

#             final_text = "\n".join(
#                 block.text
#                 for block in response.content
#                 if block.type == "text"
#             )


#             return {
#                 "messages": updated_messages,
#                 "final_diagnosis": final_text,
#                 "pending_tool_calls": []
#                 #"pending_tool_name": block.name,
#                 #"pending_tool_input": block.input
#             }


def approval_node(state: IncidentState):
    print("\n[Graph] Human approval required")

    print(
        f"Recommended action: rollback {state['service_name']} "
        f"to the previous version"
    )

    answer = input("Approve rollback? (yes/no): ").strip().lower()

    if answer in {"yes", "y"}:
        return {
            "approval_required": True,
            "approval_status": "APPROVED"
        }

    return {
        "approval_required": True,
        "approval_status": "REJECTED"
    }


def execute_action_node(state: IncidentState):
    print("\n[Graph] Executing approved action")

    result = rollback_deployment(
        state["service_name"]
    )

    print(f"[Graph] Action result: {result}")

    return {
        "action_executed": True,
          "tools_used": state["tools_used"] + [
            "rollback_deployment"
        ],
        "evidence": state["evidence"] + [
            {
                "tool": "rollback_deployment",
                "input": {
                    "service_name": state["service_name"]
                },
                "result": result
            }
        ]
    }
def execute_tool_node(state: IncidentState):

    pending_calls = state["pending_tool_calls"]
    print(
        f"\n[Graph] Total pending tool calls to execute: "
        f"{len(pending_calls)}"
    )
    tool_results = []
    tools_used = state["tools_used"]
    evidence = state["evidence"]
    #tool_name = state["pending_tool_name"]
    #tool_input = state["pending_tool_input"]

    for tool_call in pending_calls:
        tool_name = tool_call["name"]
        tool_input = tool_call["input"]
        tool_use_id = tool_call["id"]
        print(f"\n[Graph] Executing tool: {tool_name}")
        print(f"[Graph] Tool input: {tool_input}")
        try:
            result = call_tool(tool_name, tool_input)

            print(f"[Graph] Tool result: {result}")

            tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": json.dumps(result)
                    })  

            evidence.append({
                "tool": tool_name,
                "input": tool_input,
                "result": result
            })

        except Exception as e:
            print(f"[Graph] Error executing tool: {e}")

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_use_id,
                "content": str(e),
                "is_error": True
            })

            evidence.append({
                "tool": tool_name,
                "input": tool_input,
                "error": str(e)
            })
        

        tools_used.append(tool_name)
        

    print(
        f"[Graph] Returning {len(tool_results)} "
        f"tool results to Claude"
    )


    return {
        "messages": state["messages"] + [
            {
                "role": "user",
                "content": tool_results
            }
        ],
        "tools_used": tools_used,
        "evidence": evidence,
        "iteration_count": state["iteration_count"] + 1,
        "pending_tool_calls": []
    }

def finalize_after_action_node(state: IncidentState):
    print("\n[Graph] Finalizing incident after remediation")

    updated_diagnosis = (
        state["final_diagnosis"]
        + "\n\n## Remediation status\n\n"
        + f"Human approval was granted. "
        + f"{state['service_name']} was successfully rolled back "
        + "from version 2.4.1 to version 2.4.0."
        + "\n\nThe next step is to verify recovery by checking "
        + "service health, error rate, and connection-pool status."
    )

    return {
        "final_diagnosis": updated_diagnosis
    }
def route_after_agent(state: IncidentState):
    if state["final_diagnosis"]:
        return "approval"

    if state["iteration_count"] >= 10:
        return "end"
    
    if state["pending_tool_calls"]:
        return "tool"

    return "end"
    
    # if state["final_diagnosis"]:
    #     return "end"

    # if state["iteration_count"] >= 10:
    #     return "end"

    # return "tool"

def route_after_approval(state: IncidentState):
    if state["approval_status"] == "APPROVED":
        return "execute"

    return "end"



builder = StateGraph(IncidentState)


builder.add_node(
    "initialize_incident",
    initialize_incident
)

builder.add_node(
    "baseline_diagnostics",
    baseline_diagnostics_node
)

builder.add_node(
    "agent",
    agent_node
)
builder.add_node(
    "execute_tool",
    execute_tool_node
)

builder.add_node(
    "approval",
    approval_node
)

builder.add_node(
    "execute_action",
    execute_action_node
)

builder.add_node(
    "finalize_after_action",
    finalize_after_action_node
)
builder.add_edge(
    START,
    "initialize_incident"
)

builder.add_edge(
    "initialize_incident",
    "baseline_diagnostics"
)

builder.add_edge(
    "baseline_diagnostics",
    "agent"
)

builder.add_conditional_edges(
    "agent",
    route_after_agent,
    {
        "tool": "execute_tool",
        "approval": "approval",
        "end": END
    }
)

builder.add_conditional_edges(
    "approval",
    route_after_approval,
    {
        "execute": "execute_action",
        "end": END
    }
)

builder.add_edge(
    "execute_action",
    "finalize_after_action"
)


builder.add_edge(
    "execute_tool",
    "agent"
)

builder.add_edge(
    "finalize_after_action",
    END
)

incident_graph = builder.compile()