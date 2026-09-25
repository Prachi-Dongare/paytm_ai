from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.merchant import Merchant


class MerchantService:
    @staticmethod
    def get_by_merchant_id(
        db: Session,
        merchant_id: str,
    ) -> Merchant | None:
        statement = select(Merchant).where(
            Merchant.merchant_id == merchant_id
        )

        return db.scalar(statement)

    @staticmethod
    def get_all(
        db: Session,
    ) -> list[Merchant]:
        statement = select(Merchant).order_by(Merchant.id)

        return list(db.scalars(statement).all())