from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.refund import Refund
from app.models.transaction import Transaction
from app.services.action_service import ActionService


SAFE_ACTIONS = {
    "INVESTIGATE_SETTLEMENT",
    "VERIFY_REFUND",
}


def execute_safe_action(
    db: Session,
    action_type: str,
    transaction_id: str,
) -> dict:

    if action_type not in SAFE_ACTIONS:
        return {
            "success": False,
            "status": "rejected",
            "error": (
                f"Action '{action_type}' is not a safe "
                "autonomous action."
            ),
        }

    transaction = db.scalar(
        select(Transaction).where(
            Transaction.transaction_id == transaction_id
        )
    )

    if transaction is None:
        return {
            "success": False,
            "status": "failed",
            "error": (
                f"Transaction '{transaction_id}' "
                "was not found."
            ),
        }

    if action_type == "INVESTIGATE_SETTLEMENT":
        return _execute_settlement_investigation(
            db=db,
            transaction=transaction,
        )

    if action_type == "VERIFY_REFUND":
        return _execute_refund_verification(
            db=db,
            transaction=transaction,
        )

    return {
        "success": False,
        "status": "rejected",
        "error": "Unsupported action.",
    }


def _execute_settlement_investigation(
    db: Session,
    transaction: Transaction,
) -> dict:

    settlement = None

    if transaction.settlements:
        settlement = transaction.settlements[0]

    if settlement is None:
        result = {
            "transaction_id": transaction.transaction_id,
            "finding": "MISSING_SETTLEMENT",
            "transaction_amount": str(transaction.amount),
            "settled_amount": "0.00",
            "difference": str(transaction.amount),
        }

    else:
        difference = (
            transaction.amount - settlement.settled_amount
        )

        result = {
            "transaction_id": transaction.transaction_id,
            "finding": (
                "SETTLEMENT_MISMATCH"
                if difference != 0
                else "SETTLEMENT_MATCH"
            ),
            "transaction_amount": str(transaction.amount),
            "settled_amount": str(
                settlement.settled_amount
            ),
            "difference": str(difference),
            "settlement_id": settlement.settlement_id,
        }

    ActionService.log_action(
        db=db,
        action_type="INVESTIGATE_SETTLEMENT",
        status="completed",
        description=(
            f"Settlement investigation completed for "
            f"{transaction.transaction_id}."
        ),
        tool_name="execution_tools.execute_safe_action",
        action_metadata=result,
    )

    return {
        "success": True,
        "status": "completed",
        "action_type": "INVESTIGATE_SETTLEMENT",
        "result": result,
    }


def _execute_refund_verification(
    db: Session,
    transaction: Transaction,
) -> dict:

    refunds = list(
        db.scalars(
            select(Refund).where(
                Refund.transaction_id == transaction.id
            )
        ).all()
    )

    completed_refunds = [
        refund
        for refund in refunds
        if refund.status == "completed"
    ]

    refund_amount = sum(
        (refund.amount for refund in completed_refunds),
        start=transaction.amount * 0,
    )

    refund_matches_transaction = (
        refund_amount == transaction.amount
    )

    result = {
        "transaction_id": transaction.transaction_id,
        "refund_count": len(completed_refunds),
        "refund_amount": str(refund_amount),
        "transaction_amount": str(transaction.amount),
        "refund_matches_transaction": (
            refund_matches_transaction
        ),
    }

    ActionService.log_action(
        db=db,
        action_type="VERIFY_REFUND",
        status="completed",
        description=(
            f"Refund verification completed for "
            f"{transaction.transaction_id}."
        ),
        tool_name="execution_tools.execute_safe_action",
        action_metadata=result,
    )

    return {
        "success": True,
        "status": "completed",
        "action_type": "VERIFY_REFUND",
        "result": result,
    }