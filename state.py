from typing import TypedDict, Optional


class IncidentState(TypedDict):
    incident: str
    service_name: str

    tools_used: list[str]
    evidence: list[dict]

    suspected_cause: Optional[str]
    recommended_action: Optional[str]

    final_diagnosis: Optional[str]

    iteration_count: int
    #pending_tool_name: Optional[str]
    #pending_tool_input: Optional[dict]
    pending_tool_calls: list[dict]
    messages: list