from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.reconciliation_case import ReconciliationCase


class CaseService:

    @staticmethod
    def get_by_case_id(
        db: Session,
        case_id: str,
    ) -> ReconciliationCase | None:

        statement = select(ReconciliationCase).where(
            ReconciliationCase.case_id == case_id
        )

        return db.scalar(statement)

    @staticmethod
    def get_open_cases(
        db: Session,
        merchant_id: int | None = None,
    ) -> list[ReconciliationCase]:

        statement = select(ReconciliationCase).where(
            ReconciliationCase.status == "open"
        )

        if merchant_id is not None:
            statement = statement.where(
                ReconciliationCase.merchant_id == merchant_id
            )

        statement = statement.order_by(
            ReconciliationCase.created_at
        )

        return list(db.scalars(statement).all())

    @staticmethod
    def create_case(
        db: Session,
        case_id: str,
        merchant_id: int,
        transaction_id: int | None,
        case_type: str,
        expected_amount,
        actual_amount,
        description: str,
        priority: str = "medium",
    ) -> ReconciliationCase:

        case = ReconciliationCase(
            case_id=case_id,
            merchant_id=merchant_id,
            transaction_id=transaction_id,
            case_type=case_type,
            expected_amount=expected_amount,
            actual_amount=actual_amount,
            status="open",
            priority=priority,
            description=description,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        db.add(case)
        db.commit()
        db.refresh(case)

        return case