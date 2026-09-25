from app.tools.execution_tools import execute_safe_action
from app.agents.action_planner import build_action_plan
from app.tools.case_creation_tools import create_reconciliation_case
from app.tools.approval_tools import request_approval
from app.services.approval_service import ApprovalService
from app.services.ai_service import AIService
from langgraph.graph import END, START, StateGraph
from sqlalchemy.orm import Session

from app.agents.state import AgentState
from app.tools.investigation_tools import investigate_discrepancy
from app.tools.merchant_tools import get_merchant
from app.tools.reconciliation_tools import reconcile_merchant


def initialize_task(state: AgentState) -> AgentState:
    return {
        **state,
        "current_step": "initialize",
        "status": "running",
        "error": None,
        "investigations": [],
    }


def load_merchant(
    state: AgentState,
    db: Session,
) -> AgentState:
    merchant_id = state["merchant_id"]

    merchant = get_merchant(
        db=db,
        merchant_id=merchant_id,
    )

    if merchant is None:
        return {
            **state,
            "current_step": "load_merchant",
            "status": "failed",
            "error": f"Merchant '{merchant_id}' was not found.",
        }

    return {
        **state,
        "merchant": merchant,
        "current_step": "load_merchant",
    }


def run_reconciliation(
    state: AgentState,
    db: Session,
) -> AgentState:
    if state.get("status") == "failed":
        return state

    merchant_id = state["merchant_id"]

    result = reconcile_merchant(
        db=db,
        merchant_id=merchant_id,
    )

    return {
        **state,
        "reconciliation_result": result,
        "current_step": "reconciliation",
    }


def investigate(
    state: AgentState,
    db: Session,
) -> AgentState:
    if state.get("status") == "failed":
        return state

    reconciliation_result = state.get(
        "reconciliation_result"
    )

    if not reconciliation_result:
        return {
            **state,
            "current_step": "investigation",
            "status": "failed",
            "error": "No reconciliation result available.",
        }

    discrepancies = reconciliation_result.get(
        "discrepancies",
        [],
    )

    investigations = []

    for discrepancy in discrepancies:
        transaction_id = discrepancy["transaction_id"]

        investigation = investigate_discrepancy(
            db=db,
            transaction_id=transaction_id,
        )

        investigation["difference"] = discrepancy["difference"]
        investigation["settlement_id"] = discrepancy["settlement_id"]
        investigation["settled_amount"] = discrepancy[
            "settled_amount"
        ]

        investigations.append(investigation)

    return {
        **state,
        "investigations": investigations,
        "current_step": "investigation",
        "status": (
            "discrepancies_found"
            if investigations
            else "no_discrepancies"
        ),
    }
    
def ai_reasoning(state: AgentState) -> AgentState:
    if state.get("status") == "failed":
        return state

    merchant = state.get("merchant")
    investigations = state.get("investigations", [])

    if merchant is None:
        return {
            **state,
            "current_step": "ai_reasoning",
            "status": "failed",
            "error": "Merchant information is unavailable.",
        }

    if not investigations:
        return {
            **state,
            "ai_analysis": {
                "analysis": "No discrepancies require investigation."
            },
            "current_step": "ai_reasoning",
        }

    try:
        ai_service = AIService()

        analysis = ai_service.analyze_reconciliation(
            merchant=merchant,
            investigations=investigations,
        )

        return {
            **state,
            "ai_analysis": analysis,
            "current_step": "ai_reasoning",
        }

    except Exception as exc:
        return {
            **state,
            "current_step": "ai_reasoning",
            "status": "failed",
            "error": f"AI reasoning failed: {exc}",
        }
        

def plan_actions(state: AgentState) -> AgentState:
    if state.get("status") == "failed":
        return state

    actions = build_action_plan(state)

    return {
        **state,
        "planned_actions": actions,
        "current_step": "action_planning",
    }
    
def execute_actions(
    state: AgentState,
    db: Session,
) -> AgentState:
    if state.get("status") == "failed":
        return state

    planned_actions = state.get("planned_actions", [])

    execution_results = []

    for action in planned_actions:
        if action.get("approval_required") is True:
            execution_results.append(
                {
                    "transaction_id": action["transaction_id"],
                    "action_type": action["action_type"],
                    "status": "waiting_for_approval",
                    "message": (
                        "Action requires human approval "
                        "before execution."
                    ),
                }
            )
            continue

        result = execute_safe_action(
            db=db,
            action_type=action["action_type"],
            transaction_id=action["transaction_id"],
        )

        execution_results.append(result)

    return {
        **state,
        "execution_results": execution_results,
        "current_step": "action_execution",
    }
    
def create_cases(
    state: AgentState,
    db: Session,
) -> AgentState:

    if state.get("status") == "failed":
        return state

    investigations = state.get(
        "investigations",
        [],
    )

    case_results = []

    for investigation in investigations:

        classification = investigation["classification"]

        if classification == "REFUND_RELATED":
            continue

        result = create_reconciliation_case(
            db=db,
            merchant_id=state["merchant_id"],
            transaction_id=investigation["transaction_id"],
            case_type=classification,
            description=investigation["reason"],
            priority=(
                "high"
                if investigation["difference"] >= 3000
                else "medium"
            ),
        )

        case_results.append(result)

    return {
        **state,
        "case_results": case_results,
        "current_step": "case_creation",
    }
    
def request_case_approvals(
    state: AgentState,
    db: Session,
) -> AgentState:

    if state.get("status") == "failed":
        return state

    case_results = state.get("case_results", [])
    approval_requests = []

    for case in case_results:

        if not case.get("success"):
            continue

        case_type = case.get("case_type")

        if case_type != "UNEXPLAINED_DISCREPANCY":
            continue

        case_db_id = case.get("case_db_id")

        if case_db_id is None:
            continue

        transaction_id = case.get("transaction_id")

        difference = next(
            (
                investigation["difference"]
                for investigation in state.get("investigations", [])
                if investigation["transaction_id"] == transaction_id
            ),
            None,
        )

        existing_approval = ApprovalService.get_active_approval(
            db=db,
            case_id=case_db_id,
        )

        if existing_approval is not None:
            approval_requests.append(
                {
                    "success": True,
                    "approval_id": existing_approval.id,
                    "case_id": existing_approval.case_id,
                    "requested_action": existing_approval.requested_action,
                    "status": existing_approval.status,
                    "reason": existing_approval.reason,
                }
            )
            continue

        approval = request_approval(
            db=db,
            case_id=case_db_id,
            requested_action="REVIEW_AND_RESOLVE_DISCREPANCY",
            reason=(
                f"Human review required for "
                f"{transaction_id} because the discrepancy "
                f"remains unexplained. "
                f"Difference: ₹{difference}."
            ),
        )

        approval_requests.append(approval)

    return {
        **state,
        "approval_requests": approval_requests,
        "current_step": "approval_request",
        "status": (
            "waiting_for_approval"
            if approval_requests
            else state.get("status", "completed")
        ),
    }


def complete_task(state: AgentState) -> AgentState:
    if state.get("status") == "failed":
        return state

    if state.get("status") == "waiting_for_approval":
        return {
            **state,
            "current_step": "complete",
            "status": "waiting_for_approval",
        }

    return {
        **state,
        "current_step": "complete",
        "status": "completed",
    }


def build_agent_graph(db: Session):
    graph = StateGraph(AgentState)

    graph.add_node(
        "initialize",
        initialize_task,
    )

    graph.add_node(
        "load_merchant",
        lambda state: load_merchant(state, db),
    )

    graph.add_node(
        "reconciliation",
        lambda state: run_reconciliation(state, db),
    )

    graph.add_node(
        "investigation",
        lambda state: investigate(state, db),
    )
    
    graph.add_node(
    "approval_request",
    lambda state: request_case_approvals(state, db),
)
    graph.add_node(
        "ai_reasoning",
        ai_reasoning,
    )
    graph.add_node(
        "action_planning",
        plan_actions,
    )
    graph.add_node(
    "action_execution",
    lambda state: execute_actions(state, db),
)

    graph.add_node(
    "case_creation",
    lambda state: create_cases(state, db),
)
    
    graph.add_node(
        "complete",
        complete_task,
    )

    graph.add_edge(
        START,
        "initialize",
    )

    graph.add_edge(
        "initialize",
        "load_merchant",
    )

    graph.add_edge(
        "load_merchant",
        "reconciliation",
    )

    graph.add_edge(
        "reconciliation",
        "investigation",
    )

    graph.add_edge(
        "investigation",
        "ai_reasoning",
    )

    graph.add_edge(
        "ai_reasoning",
        "action_planning",
    )

    graph.add_edge(
    "action_planning",
    "action_execution",
)
    graph.add_edge(
    "action_execution",
    "case_creation",
)
    
    graph.add_edge(
    "case_creation",
    "approval_request",
)
    graph.add_edge(
    "approval_request",
    "complete",
)

    graph.add_edge(
        "complete",
        END,
    )

    return graph.compile()