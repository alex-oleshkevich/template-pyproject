from starception import install_error_handler
from starlette.applications import Starlette

from {{cookiecutter.project_name}}.base.localization import setup_translator
from {{cookiecutter.project_name}}.config.database import db
from {{cookiecutter.project_name}}.config.errors import error_handlers
from {{cookiecutter.project_name}}.config.mails import mails
from {{cookiecutter.project_name}}.config.middleware import middleware
from {{cookiecutter.project_name}}.config.routes import routes
from {{cookiecutter.project_name}}.config.sentry import setup_sentry
from {{cookiecutter.project_name}}.config.settings import Settings, settings
from {{cookiecutter.project_name}}.config.templating import templates

install_error_handler()


def create_app(settings: Settings) -> Starlette:
    app = Starlette(
        routes=routes,
        debug=settings.debug,
        middleware=middleware,
        exception_handlers=error_handlers,
        on_startup=[setup_sentry, setup_translator],
    )
    db.setup(app)
    mails.setup(app)
    templates.setup(app)
    return app


app = create_app(settings)
