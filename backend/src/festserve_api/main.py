from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from festserve_api.health import router as health_router
import os

app = FastAPI()

# Register API routes first
app.include_router(health_router, prefix="/api")

# Mount the built React app at root (this must be last)
local_static = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../static"))
docker_static = "/app/static"
static_dir = local_static if os.path.exists(local_static) else docker_static
app.mount(
    "/",
    StaticFiles(directory=static_dir, html=True),
    name="static",
)