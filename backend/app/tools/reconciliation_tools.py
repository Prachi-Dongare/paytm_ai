from sqlalchemy.orm import Session

from app.services.reconciliation_service import (
    ReconciliationService,
)


def reconcile_merchant(
    db: Session,
    merchant_id: str,
) -> dict:
    pairs = ReconciliationService.get_transaction_settlement_pairs(
        db=db,
        merchant_id=merchant_id,
    )

    discrepancies = [
        pair
        for pair in pairs
        if pair["difference"] != 0
    ]

    return {
        "merchant_id": merchant_id,
        "total_transactions": len(pairs),
        "discrepancy_count": len(discrepancies),
        "discrepancies": discrepancies,
    }