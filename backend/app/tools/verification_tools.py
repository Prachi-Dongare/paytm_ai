from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.reconciliation_case import ReconciliationCase
from app.models.settlement import Settlement
from app.models.transaction import Transaction
from app.services.action_service import ActionService


def verify_settlement_adjustment(
    db: Session,
    case_id: int,
) -> dict:

    case = db.scalar(
        select(ReconciliationCase).where(
            ReconciliationCase.id == case_id
        )
    )

    if case is None:
        return {
            "success": False,
            "status": "failed",
            "error": f"Case '{case_id}' was not found.",
        }

    transaction = db.scalar(
        select(Transaction).where(
            Transaction.id == case.transaction_id
        )
    )

    if transaction is None:
        return {
            "success": False,
            "status": "failed",
            "error": "Transaction associated with the case was not found.",
        }

    settlement = db.scalar(
        select(Settlement).where(
            Settlement.transaction_id == transaction.id
        )
    )

    if settlement is None:
        return {
            "success": False,
            "status": "failed",
            "error": "Settlement was not found.",
        }

    difference = (
        transaction.amount
        - settlement.settled_amount
    )

    verified = difference == Decimal("0.00")

    if verified:
        case.status = "resolved"
    else:
        case.status = "open"

    db.commit()

    action = ActionService.log_action(
        db=db,
        action_type="VERIFY_SETTLEMENT",
        status="completed" if verified else "failed",
        description=(
            f"Settlement verification for "
            f"{transaction.transaction_id}."
        ),
        case_id=case.id,
        tool_name="verification_tools.verify_settlement_adjustment",
        action_metadata={
            "transaction_id": transaction.transaction_id,
            "transaction_amount": str(transaction.amount),
            "settled_amount": str(settlement.settled_amount),
            "remaining_difference": str(difference),
            "verified": verified,
        },
    )

    return {
        "success": verified,
        "status": "verified" if verified else "verification_failed",
        "case_id": case.id,
        "transaction_id": transaction.transaction_id,
        "transaction_amount": str(transaction.amount),
        "settled_amount": str(settlement.settled_amount),
        "remaining_difference": str(difference),
        "case_status": case.status,
        "action_id": action.id,
    }