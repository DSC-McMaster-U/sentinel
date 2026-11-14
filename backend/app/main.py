from fastapi import FastAPI
from app.api.routes.health import router as health_router

app = FastAPI(title="Sentinel API")
app.include_router(health_router)
