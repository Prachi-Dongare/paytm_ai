from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.agent_action import AgentAction


class ActionHistoryService:

    @staticmethod
    def get_actions(
        db: Session,
        case_id: int | None = None,
    ) -> list[AgentAction]:

        statement = select(AgentAction)

        if case_id is not None:
            statement = statement.where(
                AgentAction.case_id == case_id
            )

        statement = statement.order_by(
            AgentAction.created_at.asc()
        )

        return list(
            db.scalars(statement).all()
        )