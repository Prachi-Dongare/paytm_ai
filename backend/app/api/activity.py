from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.agent_action import AgentAction


router = APIRouter(
    prefix="/api/activity",
    tags=["Activity"],
)


@router.get("")
def get_activity(
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
):
    statement = (
        select(AgentAction)
        .order_by(
            AgentAction.created_at.desc()
        )
        .limit(limit)
    )

    actions = list(
        db.scalars(statement).all()
    )

    return {
        "success": True,
        "count": len(actions),
        "activities": [
            {
                "id": action.id,
                "action_type": action.action_type,
                "status": action.status,
                "description": action.description,
                "tool_name": action.tool_name,
                "case_id": action.case_id,
                "metadata": action.action_metadata,
                "created_at": (
                    action.created_at.isoformat()
                    if isinstance(
                        action.created_at,
                        datetime,
                    )
                    else action.created_at
                ),
            }
            for action in actions
        ],
    }