from kupala.applications import Kupala
from kupala.contrib.babel import BabelExtension
from kupala.contrib.sentry import SentryExtension
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from starception import install_error_handler
from starlette.applications import Starlette

from {{cookiecutter.project_name}}.config.database import db
from {{cookiecutter.project_name}}.config.errors import error_handlers
from {{cookiecutter.project_name}}.config.mails import mails
from {{cookiecutter.project_name}}.config.middleware import middleware
from {{cookiecutter.project_name}}.config.routes import routes
from {{cookiecutter.project_name}}.config.settings import Settings, settings

install_error_handler()


def create_app(settings: Settings) -> Starlette:
    app = Kupala(
        routes=routes,
        debug=settings.debug,
        middleware=middleware,
        exception_handlers=error_handlers,
        extensions=[
            BabelExtension(translation_dirs=[settings.package_dir / "locales"]),
            SentryExtension(
                dsn=settings.sentry.dsn,
                environment=settings.environment,
                release_id=settings.release.release_id,
                sentry_options=dict(
                    traces_sample_rate=0.1,
                ),
                integrations=[
                    CeleryIntegration(),
                    RedisIntegration(),
                    StarletteIntegration(),
                    SqlalchemyIntegration(),
                    HttpxIntegration(),
                ],
            ),
        ],
    )
    db.setup(app)
    mails.setup(app)
    return app


app = create_app(settings)
