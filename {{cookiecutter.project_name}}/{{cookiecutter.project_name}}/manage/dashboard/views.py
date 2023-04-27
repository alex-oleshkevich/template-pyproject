from kupala.routing import Routes
from starlette.requests import Request
from starlette.responses import Response
from starlette_babel import gettext_lazy as _

from {{cookiecutter.project_name}}.config.templating import templates

routes = Routes()


@routes.get("/", name="manage")
@routes.get("/dashboard", name="manage.dashboard")
async def dashboard_view(request: Request) -> Response:
    return templates.TemplateResponse(
        request,
        "manage/dashboard/index.html",
        {
            "page_title": _("Dashboard"),
        },
    )
