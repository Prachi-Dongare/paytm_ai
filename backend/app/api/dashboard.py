from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database.connection import get_db

from app.models.agent_action import AgentAction
from app.models.approval import Approval
from app.models.reconciliation_case import ReconciliationCase
from app.models.settlement import Settlement
from app.models.transaction import Transaction


router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"],
)


# ============================================================
# OVERVIEW
# ============================================================

@router.get("/overview")
def get_dashboard_overview(
    db: Session = Depends(get_db),
):
    """
    Return the summary information used by the main dashboard.
    """

    transaction_count = (
        db.scalar(
            select(func.count(Transaction.id))
        )
        or 0
    )

    exception_count = (
        db.scalar(
            select(func.count(ReconciliationCase.id))
        )
        or 0
    )

    open_exception_count = (
        db.scalar(
            select(func.count(ReconciliationCase.id)).where(
                ReconciliationCase.status == "open"
            )
        )
        or 0
    )

    resolved_exception_count = (
        db.scalar(
            select(func.count(ReconciliationCase.id)).where(
                ReconciliationCase.status == "resolved"
            )
        )
        or 0
    )

    pending_approval_count = (
        db.scalar(
            select(func.count(Approval.id)).where(
                Approval.status == "pending"
            )
        )
        or 0
    )

    completed_action_count = (
        db.scalar(
            select(func.count(AgentAction.id)).where(
                AgentAction.status == "completed"
            )
        )
        or 0
    )

    failed_action_count = (
        db.scalar(
            select(func.count(AgentAction.id)).where(
                AgentAction.status == "failed"
            )
        )
        or 0
    )

    return {
        "merchant_id": "M101",
        "merchant_name": "Demo Merchant",

        "transactions": transaction_count,

        "exceptions": exception_count,
        "open_exceptions": open_exception_count,
        "resolved_exceptions": resolved_exception_count,

        "pending_approvals": pending_approval_count,

        "completed_actions": completed_action_count,
        "failed_actions": failed_action_count,

        "system_status": "operational",
    }


# ============================================================
# EXCEPTIONS
# ============================================================

@router.get("/exceptions")
def get_dashboard_exceptions(
    db: Session = Depends(get_db),
):
    """
    Return reconciliation cases with their latest
    transaction and settlement information.
    """

    statement = (
        select(ReconciliationCase)
        .order_by(
            ReconciliationCase.created_at.desc()
        )
    )

    cases = list(
        db.scalars(statement).all()
    )

    results = []

    for case in cases:

        expected = (
            case.expected_amount
            if case.expected_amount is not None
            else Decimal("0.00")
        )

        actual = Decimal("0.00")

        transaction_id = None

        # ----------------------------------------------------
        # Find transaction
        # ----------------------------------------------------

        if case.transaction_id is not None:

            transaction = db.scalar(
                select(Transaction).where(
                    Transaction.id == case.transaction_id
                )
            )

            if transaction is not None:

                transaction_id = (
                    transaction.transaction_id
                )

                expected = transaction.amount

                # ------------------------------------------------
                # Find latest settlement
                # ------------------------------------------------

                settlement = db.scalar(
                    select(Settlement)
                    .where(
                        Settlement.transaction_id
                        == transaction.id
                    )
                    .order_by(
                        Settlement.id.desc()
                    )
                )

                if settlement is not None:
                    actual = (
                        settlement.settled_amount
                    )

        difference = expected - actual

        results.append(
            {
                "id": case.id,

                "case_id": case.case_id,

                "transaction_id": transaction_id,

                "case_type": case.case_type,

                "expected_amount": str(
                    expected
                ),

                "actual_amount": str(
                    actual
                ),

                "difference": str(
                    difference
                ),

                "status": case.status,

                "priority": case.priority,

                "description": case.description,

                "created_at": (
                    case.created_at.isoformat()
                    if case.created_at
                    else None
                ),

                "updated_at": (
                    case.updated_at.isoformat()
                    if case.updated_at
                    else None
                ),
            }
        )

    return {
        "count": len(results),
        "exceptions": results,
    }


# ============================================================
# ACTIVITY
# ============================================================

@router.get("/activity")
def get_dashboard_activity(
    db: Session = Depends(get_db),
):
    """
    Return the latest AI teammate actions.
    """

    statement = (
        select(AgentAction)
        .order_by(
            AgentAction.created_at.desc()
        )
        .limit(50)
    )

    actions = list(
        db.scalars(statement).all()
    )

    results = []

    for action in actions:

        results.append(
            {
                "id": action.id,

                "case_id": action.case_id,

                "action_type": action.action_type,

                "status": action.status,

                "description": action.description,

                "tool_name": action.tool_name,

                "metadata": action.action_metadata,

                "created_at": (
                    action.created_at.isoformat()
                    if action.created_at
                    else None
                ),
            }
        )

    return {
        "count": len(results),
        "actions": results,
    }