import datetime
import os

from kupala.routing import Routes
from starlette.requests import Request
from starlette.responses import JSONResponse

from {{cookiecutter.project_name}}.config.settings import settings

BOOT_TIME = datetime.datetime.now()
routes = Routes()


@routes("/health")
async def healthcheck_view(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok"})


@routes.route("/version")
async def version_view(request: Request) -> JSONResponse:
    """Privacy Policy page."""
    return JSONResponse(
        {
            "env": settings.environment,
            "debug": settings.debug,
            "release_id": os.environ.get("RELEASE_ID", "-"),
            "branch": os.environ.get("CI_COMMIT_REF_SLUG", "-"),
            "commit": os.environ.get("CI_COMMIT_SHA", "-"),
            "build_date": os.environ.get("CI_BUILD_DATE", "-"),
            "boot_time": BOOT_TIME.isoformat(),
        }
    )
