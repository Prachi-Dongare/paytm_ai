from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.action_history_service import ActionHistoryService


router = APIRouter(
    prefix="/api/actions",
    tags=["Agent Actions"],
)


@router.get("")
def get_agent_actions(
    case_id: int | None = None,
    db: Session = Depends(get_db),
):
    actions = ActionHistoryService.get_actions(
        db=db,
        case_id=case_id,
    )

    return {
        "count": len(actions),
        "actions": [
            {
                "id": action.id,
                "case_id": action.case_id,
                "action_type": action.action_type,
                "status": action.status,
                "description": action.description,
                "tool_name": action.tool_name,
                "metadata": action.action_metadata,
                "created_at": action.created_at,
            }
            for action in actions
        ],
    }