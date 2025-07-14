from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.asyncio import AsyncIOScheduler


# from festserve_api.health import router as health_router
from festserve_api.health import health_router
from festserve_api.auth import router as auth_router
from festserve_api.routes.campaigns import router as campaigns_router
from festserve_api.routes.scan_events import router as scan_events_router
from festserve_api.tasks import snapshot_all_campaigns


import os

app = FastAPI()

# Register API routes first
app.include_router(health_router, prefix="/api")
app.include_router(auth_router)
app.include_router(campaigns_router)
app.include_router(scan_events_router)


from fastapi import Depends
from festserve_api.auth import get_current_user

@app.get("/api/dashboard")
def read_dashboard(current_user = Depends(get_current_user)):
    identifier = (
        current_user.contact_email
        if hasattr(current_user, "contact_email")
        else current_user.username
    )
    return {"msg": f"Welcome, {identifier}!"}

# Mount the built React app at root (this must be last)
local_static = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../static"))
docker_static = "/app/static"
static_dir = local_static if os.path.exists(local_static) else docker_static
app.mount(
    "/",
    StaticFiles(directory=static_dir, html=True),
    name="static",
)

# On startup, spin up an AsyncIO scheduler
@app.on_event("startup")
async def start_snapshot_scheduler():
    scheduler = AsyncIOScheduler()
    
    # every hour on the hour:
    scheduler.add_job(snapshot_all_campaigns, "cron", minute=0)

    # during development: run once every minute
    #scheduler.add_job(snapshot_all_campaigns, "cron", minute="*")
    
    scheduler.start()

# (Optionally, on shutdown you can shut it down)
@app.on_event("shutdown")
async def shutdown_snapshot_scheduler():
    for job in AsyncIOScheduler().get_jobs():
        job.remove()
