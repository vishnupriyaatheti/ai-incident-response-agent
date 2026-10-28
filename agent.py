import json
from anthropic import Anthropic
from dotenv import load_dotenv

from tools import (
    get_service_health,
    get_recent_logs,
    check_database_health,
    get_recent_deployments,
)

load_dotenv()

client = Anthropic()


TOOLS = [
    {
        "name": "get_service_health",
        "description": (
            "Get the current health information for a microservice, "
            "including status, response time, and error rate."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "service_name": {
                    "type": "string",
                    "description": "Name of the microservice to investigate."
                }
            },
            "required": ["service_name"]
        }
    },
    {
        "name": "get_recent_logs",
        "description": (
            "Retrieve recent application logs for a microservice "
            "to investigate failures and unusual behavior."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "service_name": {
                    "type": "string",
                    "description": "Name of the microservice."
                },
                "minutes": {
                    "type": "integer",
                    "description": "Number of recent minutes of logs to retrieve."
                }
            },
            "required": ["service_name", "minutes"]
        }
    },
    {
        "name": "check_database_health",
        "description": (
            "Check the health of the database associated with a microservice."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "service_name": {
                    "type": "string",
                    "description": "Name of the microservice."
                }
            },
            "required": ["service_name"]
        }
    },
    {
        "name": "get_recent_deployments",
        "description": (
            "Retrieve recent deployment information for a microservice "
            "to determine whether a deployment could be related to an incident."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "service_name": {
                    "type": "string",
                    "description": "Name of the microservice."
                }
            },
            "required": ["service_name"]
        }
    }
]


def call_tool(name, tool_input):
    if name == "get_service_health":
        return get_service_health(**tool_input)

    if name == "get_recent_logs":
        return get_recent_logs(**tool_input)

    if name == "check_database_health":
        return check_database_health(**tool_input)

    if name == "get_recent_deployments":
        return get_recent_deployments(**tool_input)

    raise ValueError(f"Unknown tool: {name}")


SYSTEM_PROMPT = """
You are an incident-response investigation agent.

Investigate microservice incidents using the available diagnostic tools.

Rules:
- Gather evidence using tools instead of guessing.
- Use additional tools when the available evidence is not enough.
- Do not invent service information.
- The available tools are read-only diagnostic tools.
- When enough evidence is available, return:
  1. Likely root cause
  2. Supporting evidence
  3. Recommended next action
- If the evidence is insufficient, clearly say so.
"""


def investigate_incident(incident):
    messages = [
        {
            "role": "user",
            "content": incident
        }
    ]

    for _ in range(10):

        response = client.messages.create(
            model="claude-haiku-5-5",
            max_tokens=1200,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages
        )

        # Add Claude's full response to conversation history.
        messages.append(
            {
                "role": "assistant",
                "content": response.content
            }
        )

        # If Claude is finished, return the text response.
        if response.stop_reason != "tool_use":
            final_text = []

            for block in response.content:
                if block.type == "text":
                    final_text.append(block.text)

            return "\n".join(final_text)

        tool_results = []

        for block in response.content:
            if block.type != "tool_use":
                continue

            print(f"\nAgent selected tool: {block.name}")
            print(f"Arguments: {block.input}")

            result = call_tool(
                block.name,
                block.input
            )

            print(f"Tool result: {result}")

            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result)
                }
            )

        # Return all tool results to Claude.
        messages.append(
            {
                "role": "user",
                "content": tool_results
            }
        )

    return "Investigation stopped because the maximum tool-call limit was reached."