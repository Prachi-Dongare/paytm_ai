from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.approval import Approval


class ApprovalService:

    @staticmethod
    def create_approval(
        db: Session,
        case_id: int,
        requested_action: str,
        reason: str,
    ) -> Approval:

        existing_approval = ApprovalService.get_active_approval(
            db=db,
            case_id=case_id,
        )

        if existing_approval is not None:
            return existing_approval

        approval = Approval(
            case_id=case_id,
            requested_action=requested_action,
            status="pending",
            reason=reason,
            created_at=datetime.utcnow(),
        )

        db.add(approval)
        db.commit()
        db.refresh(approval)

        return approval

    @staticmethod
    def get_pending_approval(
        db: Session,
        case_id: int,
    ) -> Approval | None:

        statement = (
            select(Approval)
            .where(
                Approval.case_id == case_id,
                Approval.status == "pending",
            )
            .order_by(Approval.created_at.desc())
        )

        return db.scalar(statement)

    @staticmethod
    def get_active_approval(
        db: Session,
        case_id: int,
    ) -> Approval | None:

        statement = (
            select(Approval)
            .where(
                Approval.case_id == case_id,
                Approval.status.in_({"pending", "approved"}),
            )
            .order_by(Approval.created_at.desc())
        )

        return db.scalar(statement)

    @staticmethod
    def resolve_approval(
        db: Session,
        approval_id: int,
        status: str,
        approved_by: str,
    ) -> Approval | None:

        statement = select(Approval).where(
            Approval.id == approval_id
        )

        approval = db.scalar(statement)

        if approval is None:
            return None

        if status not in {"approved", "rejected"}:
            raise ValueError(
                "Approval status must be "
                "'approved' or 'rejected'."
            )

        approval.status = status
        approval.approved_by = approved_by
        approval.resolved_at = datetime.utcnow()

        db.commit()
        db.refresh(approval)

        return approval