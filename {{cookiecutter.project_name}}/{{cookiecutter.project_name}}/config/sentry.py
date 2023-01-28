import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

from {{cookiecutter.project_name}}.config.settings import settings


def setup_sentry() -> None:
    if settings.sentry.dsn:
        sentry_sdk.init(
            settings.sentry.dsn,
            traces_sample_rate=settings.sentry.traces_sample_rate,
            environment=settings.environment,
            release=settings.release.release_id,
            integrations=[
                CeleryIntegration(),
                RedisIntegration(),
                StarletteIntegration(),
                SqlalchemyIntegration(),
                HttpxIntegration(),
            ],
        )
