from app.database.connection import SessionLocal
from app.models.merchant import Merchant


def seed_test_merchant() -> None:
    db = SessionLocal()

    try:
        existing = (
            db.query(Merchant)
            .filter(Merchant.merchant_id == "M101")
            .first()
        )

        if existing is None:
            merchant = Merchant(
                merchant_id="M101",
                name="Demo Merchant",
                category="Retail",
                status="active",
            )

            db.add(merchant)
            db.commit()

            print("Test merchant M101 created.")
        else:
            print("Test merchant M101 already exists.")

    finally:
        db.close()


if __name__ == "__main__":
    seed_test_merchant()