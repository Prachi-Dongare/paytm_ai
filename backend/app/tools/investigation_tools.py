from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.refund import Refund
from app.models.transaction import Transaction


def investigate_discrepancy(
    db: Session,
    transaction_id: str,
) -> dict:
    transaction = db.scalar(
        select(Transaction).where(
            Transaction.transaction_id == transaction_id
        )
    )

    if transaction is None:
        return {
            "transaction_id": transaction_id,
            "classification": "UNKNOWN",
            "reason": "Transaction was not found.",
        }

    refunds = list(
        db.scalars(
            select(Refund).where(
                Refund.transaction_id == transaction.id
            )
        ).all()
    )

    refund_amount = sum(
        (refund.amount for refund in refunds),
        start=transaction.amount * 0,
    )

    if refunds and refund_amount >= transaction.amount:
        classification = "REFUND_RELATED"
        reason = (
            "A completed refund explains the difference "
            "between the transaction and settlement."
        )

    elif transaction.status == "success":
        classification = "UNEXPLAINED_DISCREPANCY"
        reason = (
            "The transaction was successful, but the settlement "
            "does not match the transaction amount."
        )

    else:
        classification = "UNKNOWN"
        reason = (
            "The discrepancy could not be classified from "
            "the available transaction data."
        )

    return {
        "transaction_id": transaction_id,
        "classification": classification,
        "reason": reason,
        "transaction_amount": transaction.amount,
        "refund_amount": refund_amount,
        "refund_count": len(refunds),
    }