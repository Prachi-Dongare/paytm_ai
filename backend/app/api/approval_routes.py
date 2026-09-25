from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.approval_query_service import ApprovalQueryService
from app.tools.approval_resolution_tools import resolve_human_approval


router = APIRouter(
    prefix="/api/approvals",
    tags=["Approvals"],
)


class ApprovalDecision(BaseModel):
    decision: str
    approved_by: str


@router.get("/pending")
def get_pending_approvals(
    db: Session = Depends(get_db),
):
    approvals = ApprovalQueryService.get_pending_approvals(
        db=db,
    )

    return {
        "count": len(approvals),
        "approvals": [
            {
                "approval_id": approval.id,
                "case_id": approval.case_id,
                "requested_action": approval.requested_action,
                "status": approval.status,
                "reason": approval.reason,
                "approved_by": approval.approved_by,
                "created_at": approval.created_at,
                "resolved_at": approval.resolved_at,
            }
            for approval in approvals
        ],
    }


@router.post("/{approval_id}/resolve")
def resolve_approval(
    approval_id: int,
    request: ApprovalDecision,
    db: Session = Depends(get_db),
):
    result = resolve_human_approval(
        db=db,
        approval_id=approval_id,
        decision=request.decision,
        approved_by=request.approved_by,
    )

    if not result["success"]:
        raise HTTPException(
            status_code=400,
            detail=result["error"],
        )

    return result