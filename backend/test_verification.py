from app.database.connection import SessionLocal
from app.tools.verification_tools import verify_settlement_adjustment


def main() -> None:
    db = SessionLocal()

    try:
        result = verify_settlement_adjustment(
            db=db,
            case_id=1,
        )

        print("\nVerification result:")
        print(result)

    finally:
        db.close()


if __name__ == "__main__":
    main()