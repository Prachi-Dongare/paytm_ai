from app.database.connection import SessionLocal
from app.tools.consequential_action_tools import (
    execute_approved_settlement_adjustment,
)


def main() -> None:
    db = SessionLocal()

    try:
        result = execute_approved_settlement_adjustment(
            db=db,
            approval_id=2,
        )

        print("\nFailure recovery test result:")
        print(result)

    finally:
        db.close()


if __name__ == "__main__":
    main()