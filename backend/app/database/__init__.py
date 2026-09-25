from app.database.connection import engine
from app.models import Base

# Import all models so SQLAlchemy registers their tables.
from app.models import (
    AgentAction,
    Approval,
    Chargeback,
    Merchant,
    ReconciliationCase,
    Refund,
    Settlement,
    Transaction,
)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database tables created successfully.")