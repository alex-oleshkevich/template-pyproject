from kupala.requests import Request
from kupala.routing import Routes
from starlette.responses import Response
from starlette_babel import gettext_lazy as _

from {{cookiecutter.project_name}}.config.templating import templates

routes = Routes()


@routes.route("/", name="home")
async def landing_view(request: Request) -> Response:
    return templates.TemplateResponse(
        request,
        "landing.html",
        {
            "page_title": _("Your next big thing"),
        },
    )


@routes.route("/terms", name="terms")
async def terms_view(request: Request) -> Response:
    """Terms of Use page."""
    return templates.TemplateResponse(
        request,
        "legal/terms.html",
        {
            "page_title": _("Terms of Use"),
        },
    )


@routes.route("/privacy-policy", name="privacy_policy")
async def privacy_policy_view(request: Request) -> Response:
    """Privacy Policy page."""
    return templates.TemplateResponse(request, "legal/privacy_policy.html", {"page_title": _("Privacy policy")})


@routes.route("/components")
async def components_view(request: Request) -> Response:
    """Privacy Policy page."""
    return templates.TemplateResponse(request, "components.html")
