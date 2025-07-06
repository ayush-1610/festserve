from fastapi import APIRouter

health_router = APIRouter()

@health_router.get("/healthz")
def health_check():
    return {"status": "ok"}