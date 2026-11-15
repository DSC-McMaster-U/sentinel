"""Create the Sentinel FastAPI app and register its health and review routes."""

from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.reviews import router as review_pull_request_router

app = FastAPI(title="Sentinel API")
app.include_router(health_router)
app.include_router(review_pull_request_router)
