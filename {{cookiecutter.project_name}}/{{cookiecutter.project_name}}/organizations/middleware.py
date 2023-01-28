from contextlib import suppress

from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from {{cookiecutter.project_name}}.models.organizations import Organization
from {{cookiecutter.project_name}}.organizations.service import get_current_organization


class OrganizationMiddleware:
    def __init__(self, app: ASGIApp, cookie_name: str = "organization_id") -> None:
        self.app = app
        self.cookie_name = cookie_name

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in {"http", "websocket"}:
            await self.app(scope, receive, send)
            return

        with suppress(TypeError, ValueError):
            request = Request(scope)
            organization_id = int(request.session.get(self.cookie_name, request.cookies.get(self.cookie_name, "")))
            if organization_id:
                request.state.organization = await Organization.get_or_none(request.state.db, organization_id)

        await self.app(scope, receive, send)


class RequireOrganizationMiddleware:
    def __init__(self, app: ASGIApp, redirect_path_name: str) -> None:
        self.app = app
        self.redirect_path_name = redirect_path_name

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in {"http", "websocket"}:
            await self.app(scope, receive, send)
            return

        request = Request(scope)
        organization = get_current_organization(request)
        if not organization:
            redirect_url = request.url_for(self.redirect_path_name)
            response = RedirectResponse(redirect_url)
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)
