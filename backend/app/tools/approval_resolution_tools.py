from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.approval import Approval
from app.services.approval_service import ApprovalService


def resolve_human_approval(
    db: Session,
    approval_id: int,
    decision: str,
    approved_by: str,
) -> dict:

    if decision not in {"approved", "rejected"}:
        return {
            "success": False,
            "error": "Decision must be 'approved' or 'rejected'.",
        }

    approval = db.scalar(
        select(Approval).where(
            Approval.id == approval_id
        )
    )

    if approval is None:
        return {
            "success": False,
            "error": f"Approval '{approval_id}' was not found.",
        }

    if approval.status != "pending":
        return {
            "success": False,
            "error": (
                f"Approval '{approval_id}' is already "
                f"{approval.status}."
            ),
        }

    resolved = ApprovalService.resolve_approval(
        db=db,
        approval_id=approval_id,
        status=decision,
        approved_by=approved_by,
    )

    if resolved is None:
        return {
            "success": False,
            "error": "Approval could not be resolved.",
        }

    return {
        "success": True,
        "approval_id": resolved.id,
        "case_id": resolved.case_id,
        "requested_action": resolved.requested_action,
        "status": resolved.status,
        "approved_by": resolved.approved_by,
        "resolved_at": resolved.resolved_at,
    }