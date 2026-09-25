from datetime import datetime

from sqlalchemy.orm import Session

from app.models.agent_action import AgentAction


class ActionService:

    @staticmethod
    def log_action(
        db: Session,
        action_type: str,
        status: str,
        description: str,
        case_id: int | None = None,
        tool_name: str | None = None,
        action_metadata: dict | None = None,
    ) -> AgentAction:

        action = AgentAction(
            case_id=case_id,
            action_type=action_type,
            status=status,
            description=description,
            tool_name=tool_name,
            action_metadata=action_metadata,
            created_at=datetime.utcnow(),
        )

        db.add(action)
        db.commit()
        db.refresh(action)

        return action