from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.merchant import Merchant
from app.models.transaction import Transaction
from app.services.case_service import CaseService


def create_reconciliation_case(
    db: Session,
    merchant_id: str,
    transaction_id: str,
    case_type: str,
    description: str,
    priority: str = "medium",
) -> dict:

    merchant = db.scalar(
        select(Merchant).where(
            Merchant.merchant_id == merchant_id
        )
    )

    if merchant is None:
        return {
            "success": False,
            "error": f"Merchant '{merchant_id}' not found.",
        }

    transaction = db.scalar(
        select(Transaction).where(
            Transaction.transaction_id == transaction_id
        )
    )

    if transaction is None:
        return {
            "success": False,
            "error": f"Transaction '{transaction_id}' not found.",
        }

    case_id = f"CASE-{transaction_id}"

    existing_case = CaseService.get_by_case_id(
        db=db,
        case_id=case_id,
    )

    if existing_case is not None:
        return {
            "success": True,
            "case_id": existing_case.case_id,
            "case_db_id": existing_case.id,
            "status": "already_exists",
            "transaction_id": transaction_id,
            "case_type": existing_case.case_type,
            "priority": existing_case.priority,
        }

    case = CaseService.create_case(
        db=db,
        case_id=case_id,
        merchant_id=merchant.id,
        transaction_id=transaction.id,
        case_type=case_type,
        expected_amount=transaction.amount,
        actual_amount=Decimal("0.00"),
        description=description,
        priority=priority,
    )

    return {
        "success": True,
        "case_id": case.case_id,
        "case_db_id": case.id,
        "status": "created",
        "transaction_id": transaction_id,
        "case_type": case_type,
        "priority": priority,
    }