from kupala.routing import Routes
from starlette.responses import Response
from starlette_babel import gettext_lazy as _

from {{cookiecutter.project_name}}.base.http import HttpRequest
from {{cookiecutter.project_name}}.config.templating import templates

routes = Routes()


@routes.get("/", name="manage")
@routes.get("/dashboard", name="manage.dashboard")
async def dashboard_view(request: HttpRequest) -> Response:
    return templates.TemplateResponse(
        request,
        "manage/dashboard/index.html",
        {
            "page_title": _("Dashboard"),
        },
    )
