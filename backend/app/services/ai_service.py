from ollama import chat

from app.core.config import settings


class AIService:
    def __init__(self) -> None:
        self.model = settings.local_ai_model

    def analyze_reconciliation(
        self,
        merchant: dict,
        investigations: list[dict],
    ) -> dict:
        prompt = f"""
You are an AI teammate responsible for merchant payment
reconciliation.

Your job is to analyze reconciliation investigation results
and produce an operational action plan.

Merchant:
{merchant}

Investigations:
{investigations}

For each discrepancy:

1. Understand the reason for the discrepancy.
2. Decide whether it is explained or unresolved.
3. Recommend the next operational action.
4. Determine whether human approval is required.

IMPORTANT RULES:

- Never invent transaction information.
- Never change transaction or settlement amounts.
- Never claim that a financial action was executed.
- Any financially consequential action MUST require human approval.
- Use only the information provided.
- Keep the response concise and operational.

Explain your reasoning clearly.
"""

        response = chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return {
            "analysis": response["message"]["content"],
            "model": self.model,
            "provider": "ollama",
        }