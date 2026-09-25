from decimal import Decimal

from app.database.connection import SessionLocal
from app.models.merchant import Merchant
from app.models.transaction import Transaction
from app.models.settlement import Settlement
from app.models.reconciliation_case import ReconciliationCase
from app.models.approval import Approval
from app.models.agent_action import AgentAction


def reset_demo():
    db = SessionLocal()

    try:
        # --------------------------------------------------
        # Find demo merchant
        # --------------------------------------------------
        merchant = (
            db.query(Merchant)
            .filter(Merchant.merchant_id == "M101")
            .first()
        )

        if merchant is None:
            print("M101 not found.")
            return

        # --------------------------------------------------
        # Find TXN-002
        # --------------------------------------------------
        transaction = (
            db.query(Transaction)
            .filter(Transaction.transaction_id == "TXN-002")
            .first()
        )

        if transaction is None:
            print("TXN-002 not found.")
            return

        # --------------------------------------------------
        # 1. Reset settlement to create ₹1000 discrepancy
        # --------------------------------------------------
        settlement = (
            db.query(Settlement)
            .filter(Settlement.transaction_id == transaction.id)
            .first()
        )

        if settlement:
            settlement.settled_amount = Decimal("1500.00")
            settlement.status = "partial"

        # --------------------------------------------------
        # 2. Find old reconciliation cases for TXN-002
        # --------------------------------------------------
        cases = (
            db.query(ReconciliationCase)
            .filter(
                ReconciliationCase.transaction_id == transaction.id
            )
            .all()
        )

        case_ids = [case.id for case in cases]

        # --------------------------------------------------
        # 3. Delete approvals first
        # --------------------------------------------------
        if case_ids:
            approvals = (
                db.query(Approval)
                .filter(Approval.case_id.in_(case_ids))
                .all()
            )

            for approval in approvals:
                db.delete(approval)

        # --------------------------------------------------
        # 4. Detach activity history from old cases
        # --------------------------------------------------
        # We KEEP AgentAction records so the Activity page
        # retains the previous demo history.
        if case_ids:
            actions = (
                db.query(AgentAction)
                .filter(AgentAction.case_id.in_(case_ids))
                .all()
            )

            for action in actions:
                action.case_id = None

        # --------------------------------------------------
        # 5. Delete old reconciliation cases
        # --------------------------------------------------
        for case in cases:
            db.delete(case)

        db.commit()

        print()
        print("=" * 60)
        print("DEMO RESET COMPLETE")
        print("=" * 60)
        print()
        print("Merchant:           M101")
        print("Transaction:        TXN-002")
        print("Transaction amount: ₹2500")
        print("Settlement amount:  ₹1500")
        print("Discrepancy:        ₹1000")
        print("Pending approval:   0")
        print()
        print("Old cases removed.")
        print("Activity history preserved.")
        print()
        print("Now run reconciliation from the dashboard.")
        print("=" * 60)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    reset_demo()