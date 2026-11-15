"""FastAPI application entry point."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database import Base, engine
from app.routers import alerts, crew, telemetry

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CosmaCare Astronaut Health API",
    version="1.0.0",
    description=(
        "Offline-first telemetry ingestion & clinical risk engine for "
        "long-duration space missions."
    ),
)

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(telemetry.router)
app.include_router(alerts.router)
app.include_router(crew.router)


@app.get("/", tags=["health"])
def root():
    return {
        "service": "CosmaCare",
        "status": "operational",
        "version": "1.0.0",
    }


@app.get("/health", tags=["health"])
def health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "ok",
            "database": "connected",
        }


    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "error",
                "database": "disconnected",
            },
        )
