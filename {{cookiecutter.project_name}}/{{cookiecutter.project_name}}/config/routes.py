from async_storages.file_server import FileServer
from kupala.authentication import LoginRequiredMiddleware
from kupala.responses import RedirectResponse
from kupala.routing import include
from starlette.middleware import Middleware
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from {{cookiecutter.project_name}}.admin import admin
from {{cookiecutter.project_name}}.base.storages import get_file_storage
from {{cookiecutter.project_name}}.healthcheck import routes as healthcheck_routes
from {{cookiecutter.project_name}}.metrics import routes as metrics_routes
from {{cookiecutter.project_name}}.organizations.middleware import LoadOrganizationMiddleware, RequireOrganizationMiddleware
from {{cookiecutter.project_name}}.organizations.views import routes as organization_routes
from {{cookiecutter.project_name}}.views import routes as public_routes

manage_middleware = [
    Middleware(LoginRequiredMiddleware),
    Middleware(LoadOrganizationMiddleware),
    Middleware(RequireOrganizationMiddleware, redirect_path_name="organizations.select"),
]

routes = [
    *public_routes,
    *healthcheck_routes,
    *metrics_routes,
    *include("{{cookiecutter.project_name}}.accounts.routes"),
    Route("/home", RedirectResponse("/manage"), name="home-redirect"),
    Mount("/superadmin", app=admin),
    Mount("/onboarding", routes=include("{{cookiecutter.project_name}}.onboarding.routes")),
    Mount("/manage", routes=include("{{cookiecutter.project_name}}.manage.routes"), middleware=manage_middleware),
    Mount("/static", app=StaticFiles(packages=[__name__.split(".")[0]]), name="static"),
    Mount("/media", app=FileServer(get_file_storage(), as_attachment=False), name="media"),
    Mount("/organizations", routes=organization_routes),
]
