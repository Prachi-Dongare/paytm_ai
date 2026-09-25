from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agents.workflow import build_agent_graph
from app.database.connection import get_db


router = APIRouter(
    prefix="/api/reconciliation",
    tags=["Reconciliation"],
)


@router.post("/run/{merchant_id}")
def run_reconciliation(
    merchant_id: str,
    db: Session = Depends(get_db),
):
    """
    Run the complete autonomous reconciliation workflow
    for a merchant.

    The workflow can finish in one of these states:

    completed
        No human approval is currently required.

    waiting_for_approval
        The AI teammate completed its investigation but
        a financially consequential action requires human approval.

    failed
        The workflow encountered an unrecoverable error.
    """

    try:
        graph = build_agent_graph(db)

        result = graph.invoke(
            {
                "task": "Reconcile merchant payments",
                "merchant_id": merchant_id,
            }
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Reconciliation workflow failed: {exc}",
        ) from exc

    status = result.get("status")

    return {
        "success": status != "failed",
        "status": status,
        "merchant_id": result.get("merchant_id"),
        "current_step": result.get("current_step"),
        "error": result.get("error"),

        "reconciliation": result.get(
            "reconciliation_result"
        ),

        "investigations": result.get(
            "investigations",
            [],
        ),

        "planned_actions": result.get(
            "planned_actions",
            [],
        ),

        "execution_results": result.get(
            "execution_results",
            [],
        ),

        "case_results": result.get(
            "case_results",
            [],
        ),

        "approval_requests": result.get(
            "approval_requests",
            [],
        ),
    }