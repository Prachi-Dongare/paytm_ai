from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.agent_action import AgentAction
from app.models.approval import Approval
from app.models.reconciliation_case import ReconciliationCase
from app.models.settlement import Settlement
from app.models.transaction import Transaction


router = APIRouter(
    prefix="/api/approvals",
    tags=["Approval Execution"],
)


@router.post("/{approval_id}/approve-and-execute")
def approve_and_execute(
    approval_id: int,
    db: Session = Depends(get_db),
):
    """
    Approve and execute a financially consequential
    reconciliation action.

    Important:
    - Human approval is required first.
    - Backend/database values are authoritative.
    - The endpoint never invents a settlement.
    - Missing settlement results in a safe execution block.
    - Successful execution is verified before reporting success.
    """

    try:
        # =========================================================
        # 1. FIND APPROVAL
        # =========================================================

        approval = db.scalar(
            select(Approval).where(
                Approval.id == approval_id
            )
        )

        if approval is None:
            return {
                "success": False,
                "status": "not_found",
                "error": (
                    f"Approval {approval_id} was not found."
                ),
            }

        # =========================================================
        # 2. CHECK APPROVAL STATUS
        # =========================================================

        if approval.status != "pending":
            return {
                "success": False,
                "status": "already_resolved",
                "error": (
                    f"Approval {approval_id} is already "
                    f"'{approval.status}'."
                ),
                "approval": {
                    "id": approval.id,
                    "status": approval.status,
                    "case_id": approval.case_id,
                },
            }

        # =========================================================
        # 3. FIND CASE
        # =========================================================

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
                    "The reconciliation case associated "
                    "with this approval was not found."
                ),
            }

        # =========================================================
        # 4. FIND TRANSACTION
        # =========================================================

        if case.transaction_id is None:
            return {
                "success": False,
                "status": "failed",
                "error": (
                    "This reconciliation case is not "
                    "linked to a transaction."
                ),
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
                "error": (
                    "The transaction associated with "
                    "this case was not found."
                ),
            }

        # =========================================================
        # 5. FIND SETTLEMENT
        # =========================================================

        settlement = db.scalar(
            select(Settlement)
            .where(
                Settlement.transaction_id
                == transaction.id
            )
            .order_by(Settlement.id.desc())
        )

        # =========================================================
        # 6. RECORD HUMAN APPROVAL
        # =========================================================

        approval.status = "approved"
        approval.approved_by = "demo_admin"
        approval.resolved_at = datetime.utcnow()

        db.commit()
        db.refresh(approval)

        # =========================================================
        # 7. MISSING SETTLEMENT
        # =========================================================

        if settlement is None:

            action = AgentAction(
                case_id=case.id,
                action_type="ADJUST_SETTLEMENT",
                status="failed",
                description=(
                    "Settlement adjustment could not be "
                    f"executed for {transaction.transaction_id}."
                ),
                tool_name=(
                    "approval_execution.approve_and_execute"
                ),
                action_metadata={
                    "approval_id": approval.id,
                    "transaction_id": (
                        transaction.transaction_id
                    ),
                    "reason": "MISSING_SETTLEMENT",
                },
                created_at=datetime.utcnow(),
            )

            db.add(action)
            db.commit()
            db.refresh(action)

            return {
                "success": False,
                "status": "execution_blocked",
                "message": (
                    "Approval was recorded, but the financial "
                    "action was blocked because no settlement "
                    "exists for this transaction."
                ),
                "approval": {
                    "id": approval.id,
                    "status": approval.status,
                    "approved_by": approval.approved_by,
                },
                "case": {
                    "id": case.id,
                    "case_id": case.case_id,
                    "status": case.status,
                },
                "transaction": {
                    "transaction_id": (
                        transaction.transaction_id
                    ),
                    "transaction_amount": str(
                        transaction.amount
                    ),
                },
                "execution": {
                    "success": False,
                    "status": "blocked",
                    "reason": "MISSING_SETTLEMENT",
                    "action_id": action.id,
                },
            }

        # =========================================================
        # 8. CALCULATE REAL ADJUSTMENT
        # =========================================================

        transaction_amount = Decimal(
            str(transaction.amount)
        )

        old_settled_amount = Decimal(
            str(settlement.settled_amount)
        )

        adjustment_amount = (
            transaction_amount
            - old_settled_amount
        )

        # =========================================================
        # 9. NOTHING TO ADJUST
        # =========================================================

        if adjustment_amount <= Decimal("0.00"):

            return {
                "success": False,
                "status": "execution_not_required",
                "message": (
                    "The settlement already matches "
                    "the transaction amount."
                ),
                "transaction_id": (
                    transaction.transaction_id
                ),
                "transaction_amount": str(
                    transaction_amount
                ),
                "settled_amount": str(
                    old_settled_amount
                ),
                "adjustment_amount": str(
                    adjustment_amount
                ),
            }

        # =========================================================
        # 10. EXECUTE ADJUSTMENT
        # =========================================================

        settlement.settled_amount = (
            old_settled_amount
            + adjustment_amount
        )

        settlement.status = "settled"

        # Update the case with the actual amount
        case.actual_amount = settlement.settled_amount

        action = AgentAction(
            case_id=case.id,
            action_type="ADJUST_SETTLEMENT",
            status="completed",
            description=(
                "Approved settlement adjustment executed "
                f"for {transaction.transaction_id}."
            ),
            tool_name=(
                "approval_execution.approve_and_execute"
            ),
            action_metadata={
                "approval_id": approval.id,
                "transaction_id": (
                    transaction.transaction_id
                ),
                "settlement_id": settlement.settlement_id,
                "old_settled_amount": str(
                    old_settled_amount
                ),
                "adjustment_amount": str(
                    adjustment_amount
                ),
                "new_settled_amount": str(
                    settlement.settled_amount
                ),
            },
            created_at=datetime.utcnow(),
        )

        db.add(action)
        db.commit()
        db.refresh(action)

        # =========================================================
        # 11. VERIFY
        # =========================================================

        db.refresh(settlement)

        verified_settled_amount = Decimal(
            str(settlement.settled_amount)
        )

        remaining_difference = (
            transaction_amount
            - verified_settled_amount
        )

        verified = (
            remaining_difference
            == Decimal("0.00")
        )

        if not verified:

            verification_action = AgentAction(
                case_id=case.id,
                action_type="VERIFY_SETTLEMENT",
                status="failed",
                description=(
                    "Settlement verification failed for "
                    f"{transaction.transaction_id}."
                ),
                tool_name=(
                    "approval_execution.verify_settlement"
                ),
                action_metadata={
                    "transaction_id": (
                        transaction.transaction_id
                    ),
                    "transaction_amount": str(
                        transaction_amount
                    ),
                    "settled_amount": str(
                        verified_settled_amount
                    ),
                    "remaining_difference": str(
                        remaining_difference
                    ),
                    "verified": False,
                },
                created_at=datetime.utcnow(),
            )

            db.add(verification_action)
            db.commit()
            db.refresh(verification_action)

            return {
                "success": False,
                "status": "verification_failed",
                "message": (
                    "The adjustment executed, but the "
                    "final settlement could not be verified."
                ),
                "execution": {
                    "success": True,
                    "action_id": action.id,
                },
                "verification": {
                    "success": False,
                    "transaction_id": (
                        transaction.transaction_id
                    ),
                    "transaction_amount": str(
                        transaction_amount
                    ),
                    "settled_amount": str(
                        verified_settled_amount
                    ),
                    "remaining_difference": str(
                        remaining_difference
                    ),
                },
            }

        # =========================================================
        # 12. MARK CASE RESOLVED
        # =========================================================

        case.status = "resolved"
        case.updated_at = datetime.utcnow()

        verification_action = AgentAction(
            case_id=case.id,
            action_type="VERIFY_SETTLEMENT",
            status="completed",
            description=(
                "Settlement verification completed for "
                f"{transaction.transaction_id}."
            ),
            tool_name=(
                "approval_execution.verify_settlement"
            ),
            action_metadata={
                "transaction_id": (
                    transaction.transaction_id
                ),
                "transaction_amount": str(
                    transaction_amount
                ),
                "settled_amount": str(
                    verified_settled_amount
                ),
                "remaining_difference": str(
                    remaining_difference
                ),
                "verified": True,
            },
            created_at=datetime.utcnow(),
        )

        db.add(verification_action)
        db.commit()
        db.refresh(verification_action)

        # =========================================================
        # 13. FINAL SUCCESS
        # =========================================================

        return {
            "success": True,
            "status": "completed",

            "approval": {
                "id": approval.id,
                "status": approval.status,
                "approved_by": approval.approved_by,
            },

            "case": {
                "id": case.id,
                "case_id": case.case_id,
                "status": case.status,
            },

            "transaction": {
                "transaction_id": (
                    transaction.transaction_id
                ),
                "transaction_amount": str(
                    transaction_amount
                ),
            },

            "execution": {
                "success": True,
                "action_id": action.id,
                "settlement_id": (
                    settlement.settlement_id
                ),
                "old_settled_amount": str(
                    old_settled_amount
                ),
                "adjustment_amount": str(
                    adjustment_amount
                ),
                "new_settled_amount": str(
                    settlement.settled_amount
                ),
            },

            "verification": {
                "success": True,
                "action_id": verification_action.id,
                "settled_amount": str(
                    verified_settled_amount
                ),
                "remaining_difference": str(
                    remaining_difference
                ),
                "verified": True,
            },
        }

    except Exception as exc:

        db.rollback()

        return {
            "success": False,
            "status": "internal_error",
            "error": str(exc),
            "message": (
                "The approval workflow encountered "
                "an unexpected error. No successful "
                "financial result was reported."
            ),
        }