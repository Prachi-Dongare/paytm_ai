from app.agents.workflow import build_agent_graph
from app.database.connection import SessionLocal


def main() -> None:
    db = SessionLocal()

    try:
        agent_graph = build_agent_graph(db)

        result = agent_graph.invoke(
            {
                "task": "Reconcile merchant payments",
                "merchant_id": "M101",
            }
        )

        print("\nAgent result:")
        print(result)

    finally:
        db.close()


if __name__ == "__main__":
    main()