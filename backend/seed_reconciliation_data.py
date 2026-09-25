from datetime import datetime, timedelta
from decimal import Decimal

from app.database.connection import SessionLocal
from app.models.merchant import Merchant
from app.models.refund import Refund
from app.models.settlement import Settlement
from app.models.transaction import Transaction


def seed_reconciliation_data() -> None:
    db = SessionLocal()

    try:
        merchant = (
            db.query(Merchant)
            .filter(Merchant.merchant_id == "M101")
            .first()
        )

        if merchant is None:
            raise RuntimeError(
                "Merchant M101 does not exist. "
                "Run seed_test.py first."
            )

        # Prevent duplicate seed data.
        existing_transaction = (
            db.query(Transaction)
            .filter(Transaction.transaction_id == "TXN-001")
            .first()
        )

        if existing_transaction is not None:
            print("Reconciliation test data already exists.")
            return

        base_time = datetime.utcnow()

        # ---------------------------------------------------------
        # TXN-001: NORMAL
        # Transaction = Settlement = ₹1000
        # ---------------------------------------------------------
        txn_001 = Transaction(
            transaction_id="TXN-001",
            merchant_id=merchant.id,
            amount=Decimal("1000.00"),
            currency="INR",
            status="success",
            payment_method="UPI",
            transaction_time=base_time,
        )

        db.add(txn_001)
        db.flush()

        settlement_001 = Settlement(
            settlement_id="SET-001",
            merchant_id=merchant.id,
            transaction_id=txn_001.id,
            gross_amount=Decimal("1000.00"),
            settled_amount=Decimal("1000.00"),
            settlement_date=base_time + timedelta(days=1),
            utr="UTR-001",
            status="settled",
        )

        db.add(settlement_001)

        # ---------------------------------------------------------
        # TXN-002: PARTIAL SETTLEMENT
        # Transaction = ₹2500
        # Settlement = ₹1500
        # Difference = ₹1000
        # ---------------------------------------------------------
        txn_002 = Transaction(
            transaction_id="TXN-002",
            merchant_id=merchant.id,
            amount=Decimal("2500.00"),
            currency="INR",
            status="success",
            payment_method="UPI",
            transaction_time=base_time + timedelta(minutes=5),
        )

        db.add(txn_002)
        db.flush()

        settlement_002 = Settlement(
            settlement_id="SET-002",
            merchant_id=merchant.id,
            transaction_id=txn_002.id,
            gross_amount=Decimal("2500.00"),
            settled_amount=Decimal("1500.00"),
            settlement_date=base_time + timedelta(days=1),
            utr="UTR-002",
            status="settled",
        )

        db.add(settlement_002)

        # ---------------------------------------------------------
        # TXN-003: REFUND RELATED
        # Transaction = ₹1800
        # Refund = ₹1800
        # Settlement = ₹0
        # ---------------------------------------------------------
        txn_003 = Transaction(
            transaction_id="TXN-003",
            merchant_id=merchant.id,
            amount=Decimal("1800.00"),
            currency="INR",
            status="success",
            payment_method="CARD",
            transaction_time=base_time + timedelta(minutes=10),
        )

        db.add(txn_003)
        db.flush()

        settlement_003 = Settlement(
            settlement_id="SET-003",
            merchant_id=merchant.id,
            transaction_id=txn_003.id,
            gross_amount=Decimal("1800.00"),
            settled_amount=Decimal("0.00"),
            settlement_date=base_time + timedelta(days=1),
            utr="UTR-003",
            status="adjusted",
        )

        db.add(settlement_003)

        refund_003 = Refund(
            refund_id="REF-003",
            transaction_id=txn_003.id,
            amount=Decimal("1800.00"),
            status="completed",
            refund_time=base_time + timedelta(hours=2),
        )

        db.add(refund_003)

        # ---------------------------------------------------------
        # TXN-004: MISSING SETTLEMENT
        # Transaction = ₹3200
        # No settlement record
        # ---------------------------------------------------------
        txn_004 = Transaction(
            transaction_id="TXN-004",
            merchant_id=merchant.id,
            amount=Decimal("3200.00"),
            currency="INR",
            status="success",
            payment_method="UPI",
            transaction_time=base_time + timedelta(minutes=15),
        )

        db.add(txn_004)

        # ---------------------------------------------------------
        # TXN-005: NORMAL
        # Transaction = Settlement = ₹750
        # ---------------------------------------------------------
        txn_005 = Transaction(
            transaction_id="TXN-005",
            merchant_id=merchant.id,
            amount=Decimal("750.00"),
            currency="INR",
            status="success",
            payment_method="WALLET",
            transaction_time=base_time + timedelta(minutes=20),
        )

        db.add(txn_005)
        db.flush()

        settlement_005 = Settlement(
            settlement_id="SET-005",
            merchant_id=merchant.id,
            transaction_id=txn_005.id,
            gross_amount=Decimal("750.00"),
            settled_amount=Decimal("750.00"),
            settlement_date=base_time + timedelta(days=1),
            utr="UTR-005",
            status="settled",
        )

        db.add(settlement_005)

        db.commit()

        print("Reconciliation test data created successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_reconciliation_data()