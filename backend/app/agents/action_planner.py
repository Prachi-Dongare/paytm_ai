from app.agents.state import AgentState


def build_action_plan(
    state: AgentState,
) -> list[dict]:

    investigations = state.get("investigations", [])

    actions = []

    for investigation in investigations:

        transaction_id = investigation["transaction_id"]
        classification = investigation["classification"]

        if classification == "REFUND_RELATED":
            actions.append(
                {
                    "transaction_id": transaction_id,
                    "action_type": "VERIFY_REFUND",
                    "reason": (
                        "Verify that the completed refund "
                        "correctly explains the settlement difference."
                    ),
                    "approval_required": False,
                }
            )

        elif classification == "UNEXPLAINED_DISCREPANCY":
            actions.append(
                {
                    "transaction_id": transaction_id,
                    "action_type": "INVESTIGATE_SETTLEMENT",
                    "reason": (
                        "Investigate why the successful transaction "
                        "does not have a matching settlement."
                    ),
                    "approval_required": False,
                }
            )

    return actions