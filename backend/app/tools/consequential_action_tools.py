from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.approval import Approval
from app.models.settlement import Settlement
from app.models.transaction import Transaction
from app.services.action_service import ActionService


def execute_approved_settlement_adjustment(
    db: Session,
    approval_id: int,
) -> dict:

    # ---------------------------------------------------------
    # 1. Load approval
    # ---------------------------------------------------------

    approval = db.scalar(
        select(Approval).where(
            Approval.id == approval_id
        )
    )

    if approval is None:
        return {
            "success": False,
            "status": "rejected",
            "error": f"Approval '{approval_id}' was not found.",
        }

    # ---------------------------------------------------------
    # 2. Verify approval status
    # ---------------------------------------------------------

    if approval.status != "approved":
        return {
            "success": False,
            "status": "rejected",
            "error": (
                f"Financial action cannot execute because "
                f"approval status is '{approval.status}'."
            ),
        }

    # ---------------------------------------------------------
    # 3. Verify requested action
    # ---------------------------------------------------------

    if approval.requested_action != "REVIEW_AND_RESOLVE_DISCREPANCY":
        return {
            "success": False,
            "status": "rejected",
            "error": (
                "This approval does not authorize "
                "settlement discrepancy resolution."
            ),
        }

    # ---------------------------------------------------------
    # 4. Load reconciliation case
    # ---------------------------------------------------------

    from app.models.reconciliation_case import ReconciliationCase

    case = db.scalar(
        select(ReconciliationCase).where(
            ReconciliationCase.id == approval.case_id
        )
    )

    if case is None:
        return {
            "success": False,
            "status": "failed",
            "error": (
                f"Reconciliation case "
                f"'{approval.case_id}' was not found."
            ),
        }

    # ---------------------------------------------------------
    # 5. Load transaction
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # 6. Load settlement
    # ---------------------------------------------------------

    settlement = db.scalar(
        select(Settlement).where(
            Settlement.transaction_id == transaction.id
        )
    )

    if settlement is None:
        action = ActionService.log_action(
            db=db,
            action_type="ADJUST_SETTLEMENT",
            status="failed",
            description=(
                f"Settlement adjustment could not be executed "
                f"for {transaction.transaction_id}."
            ),
            case_id=case.id,
            tool_name=(
                "consequential_action_tools."
                "execute_approved_settlement_adjustment"
            ),
            action_metadata={
                "approval_id": approval.id,
                "transaction_id": transaction.transaction_id,
                "reason": "MISSING_SETTLEMENT",
            },
        )

        return {
            "success": False,
            "status": "failed",
            "error": (
                "No settlement exists for this transaction. "
                "A settlement adjustment cannot be performed."
            ),
            "action_id": action.id,
        }

    # ---------------------------------------------------------
    # 7. Calculate adjustment deterministically
    # ---------------------------------------------------------

    difference = (
        transaction.amount
        - settlement.settled_amount
    )

    if difference <= Decimal("0.00"):
        return {
            "success": False,
            "status": "rejected",
            "error": (
                "No positive settlement discrepancy "
                "exists for this transaction."
            ),
        }

    old_settled_amount = settlement.settled_amount

    new_settled_amount = (
        old_settled_amount + difference
    )

    # ---------------------------------------------------------
    # 8. Perform approved sandbox adjustment
    # ---------------------------------------------------------

    settlement.settled_amount = new_settled_amount
    settlement.status = "settled"

    case.status = "resolved"

    db.commit()

    # ---------------------------------------------------------
    # 9. Log execution
    # ---------------------------------------------------------

    action = ActionService.log_action(
        db=db,
        action_type="ADJUST_SETTLEMENT",
        status="completed",
        description=(
            f"Approved settlement adjustment executed for "
            f"{transaction.transaction_id}."
        ),
        case_id=case.id,
        tool_name=(
            "consequential_action_tools."
            "execute_approved_settlement_adjustment"
        ),
        action_metadata={
            "approval_id": approval.id,
            "transaction_id": transaction.transaction_id,
            "settlement_id": settlement.settlement_id,
            "old_settled_amount": str(old_settled_amount),
            "adjustment_amount": str(difference),
            "new_settled_amount": str(new_settled_amount),
            "approved_by": approval.approved_by,
        },
    )

    return {
        "success": True,
        "status": "completed",
        "approval_id": approval.id,
        "case_id": case.id,
        "transaction_id": transaction.transaction_id,
        "settlement_id": settlement.settlement_id,
        "old_settled_amount": str(old_settled_amount),
        "adjustment_amount": str(difference),
        "new_settled_amount": str(new_settled_amount),
        "case_status": case.status,
        "action_id": action.id,
    }