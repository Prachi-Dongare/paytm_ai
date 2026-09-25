from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.merchant import Merchant
from app.models.settlement import Settlement
from app.models.transaction import Transaction


class ReconciliationService:
    @staticmethod
    def get_transaction_settlement_pairs(
        db: Session,
        merchant_id: str,
    ) -> list[dict]:
        merchant = db.scalar(
            select(Merchant).where(
                Merchant.merchant_id == merchant_id
            )
        )

        if merchant is None:
            return []

        statement = (
            select(Transaction, Settlement)
            .join(
                Settlement,
                Settlement.transaction_id == Transaction.id,
                isouter=True,
            )
            .where(Transaction.merchant_id == merchant.id)
            .order_by(Transaction.transaction_time)
        )

        results = []

        for transaction, settlement in db.execute(statement).all():
            settled_amount = (
                settlement.settled_amount
                if settlement is not None
                else Decimal("0.00")
            )

            difference = transaction.amount - settled_amount

            results.append(
                {
                    "transaction_id": transaction.transaction_id,
                    "transaction_amount": transaction.amount,
                    "settlement_id": (
                        settlement.settlement_id
                        if settlement is not None
                        else None
                    ),
                    "settled_amount": settled_amount,
                    "difference": difference,
                    "transaction_status": transaction.status,
                    "settlement_status": (
                        settlement.status
                        if settlement is not None
                        else None
                    ),
                }
            )

        return results