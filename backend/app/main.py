from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.approval_routes import router as approval_router
from app.api.action_routes import router as action_router
from app.api.dashboard import router as dashboard_router
from app.api.reconciliation import router as reconciliation_router
from app.api.activity import router as activity_router
from sqlalchemy import text

from app.core.config import settings
from app.database.connection import engine


app = FastAPI(
    title=settings.app_name,
    description="Autonomous Merchant Reconciliation Teammate",
    version=settings.app_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.approval_execution import (
    router as approval_execution_router,
)

app.include_router(
    approval_execution_router
)
app.include_router(dashboard_router)
app.include_router(approval_router)
app.include_router(action_router)
app.include_router(reconciliation_router)
app.include_router(approval_execution_router)
app.include_router(activity_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.environment,
    }


@app.get("/health/database")
def database_health_check():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        result.scalar_one()

    return {
        "status": "ok",
        "database": "connected",
    }