from sqlalchemy.orm import Session

from app.services.action_service import ActionService


SAFE_ACTIONS = {
    "INVESTIGATE_SETTLEMENT",
    "VERIFY_REFUND",
    "CREATE_RECONCILIATION_CASE",
}

CONSEQUENTIAL_ACTIONS = {
    "ADJUST_SETTLEMENT",
    "ISSUE_REFUND",
    "CHANGE_TRANSACTION_AMOUNT",
}


def plan_action(
    db: Session,
    action_type: str,
    transaction_id: str,
    description: str,
) -> dict:

    if action_type in CONSEQUENTIAL_ACTIONS:
        approval_required = True
    elif action_type in SAFE_ACTIONS:
        approval_required = False
    else:
        return {
            "success": False,
            "error": f"Unknown action type: {action_type}",
        }

    action = ActionService.log_action(
        db=db,
        action_type=action_type,
        status="planned",
        description=description,
        tool_name="action_tools.plan_action",
        action_metadata={
            "transaction_id": transaction_id,
            "approval_required": approval_required,
        },
    )

    return {
        "success": True,
        "action_id": action.id,
        "action_type": action_type,
        "transaction_id": transaction_id,
        "approval_required": approval_required,
        "status": "planned",
    }