from sqlalchemy.orm import Session

from app.services.case_service import CaseService


def get_open_cases(
    db: Session,
    merchant_id: int | None = None,
) -> list[dict]:
    cases = CaseService.get_open_cases(
        db=db,
        merchant_id=merchant_id,
    )

    return [
        {
            "case_id": case.case_id,
            "case_type": case.case_type,
            "status": case.status,
            "priority": case.priority,
            "description": case.description,
        }
        for case in cases
    ]