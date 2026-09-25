from typing import TypedDict


class AgentState(TypedDict, total=False):
    merchant_id: str
    task: str

    merchant: dict | None

    reconciliation_result: dict | None
    investigations: list[dict] | None

    ai_analysis: dict | None
    planned_actions: list[dict] | None
    execution_results: list[dict] | None
    case_results: list[dict] | None
    approval_requests: list[dict] | None

    current_step: str
    status: str
    error: str | None