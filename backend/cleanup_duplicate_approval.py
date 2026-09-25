from datetime import datetime

from sqlalchemy import select

from app.database.connection import SessionLocal
from app.models.approval import Approval


def cleanup_duplicate_approval() -> None:
    db = SessionLocal()
    try:
        statement = (
            select(Approval)
            .where(Approval.case_id == 2)
            .order_by(Approval.created_at.asc(), Approval.id.asc())
        )

        approvals = list(db.scalars(statement).all())

        if len(approvals) <= 1:
            print("No duplicate approval found.")
            return

        keep_approval = approvals[0]
        duplicate_approvals = approvals[1:]

        print(f"Keeping Approval #{keep_approval.id}")

        for duplicate in duplicate_approvals:
            duplicate.status = "rejected"
            duplicate.approved_by = "system_cleanup"
            duplicate.resolved_at = datetime.utcnow()
            print(f"Marked duplicate Approval #{duplicate.id} as rejected.")

        db.commit()
        print("Duplicate approval cleanup completed.")

    finally:
        db.close()


if __name__ == "__main__":
    cleanup_duplicate_approval()
