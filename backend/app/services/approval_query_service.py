from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.approval import Approval


class ApprovalQueryService:

    @staticmethod
    def get_pending_approvals(
        db: Session,
    ) -> list[Approval]:

        statement = (
            select(Approval)
            .where(
                Approval.status == "pending"
            )
            .order_by(
                Approval.created_at.asc()
            )
        )

        return list(
            db.scalars(statement).all()
        )