from sqlalchemy.orm import Session

from app.services.merchant_service import MerchantService


def get_merchant(
    db: Session,
    merchant_id: str,
) -> dict | None:
    merchant = MerchantService.get_by_merchant_id(
        db=db,
        merchant_id=merchant_id,
    )

    if merchant is None:
        return None

    return {
        "merchant_id": merchant.merchant_id,
        "name": merchant.name,
        "category": merchant.category,
        "status": merchant.status,
    }