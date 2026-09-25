from sqlalchemy.orm import Session

from app.services.approval_service import ApprovalService


def request_approval(
    db: Session,
    case_id: int,
    requested_action: str,
    reason: str,
) -> dict:

    approval = ApprovalService.create_approval(
        db=db,
        case_id=case_id,
        requested_action=requested_action,
        reason=reason,
    )

    return {
        "success": True,
        "approval_id": approval.id,
        "case_id": approval.case_id,
        "requested_action": approval.requested_action,
        "status": approval.status,
        "reason": approval.reason,
    }