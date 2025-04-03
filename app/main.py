import logging

from fastapi import FastAPI, Response

from app.db import init_db
from app.routes.metrics import router
from app.services.github_scraper import GitHubService

favicon_path = "favicon.ico"  # Adjust path to file


gitHubService = GitHubService()

logger = logging.getLogger(__name__)


init_db()
gitHubService.start_scheduler()

app = FastAPI()
app.include_router(router)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(favicon_path)
