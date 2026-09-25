from app.database.connection import SessionLocal
from app.tools.approval_resolution_tools import resolve_human_approval


def main() -> None:
    db = SessionLocal()

    try:
        result = resolve_human_approval(
            db=db,
            approval_id=1,
            decision="approved",
            approved_by="demo_admin",
        )

        print("\nApproval result:")
        print(result)

    finally:
        db.close()


if __name__ == "__main__":
    main()