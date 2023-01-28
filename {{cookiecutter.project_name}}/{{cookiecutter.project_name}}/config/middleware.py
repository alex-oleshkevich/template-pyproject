from kupala.authentication import ChoiceBackend, RememberMeBackend, SessionBackend
from kupala.contrib.sqlalchemy.authentication import UserLoader
from kupala.contrib.sqlalchemy.middleware import DbSessionMiddleware
from kupala.middleware import RequestLimitMiddleware
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette_babel import LocaleMiddleware, TimezoneMiddleware
from starsessions import CookieStore, SessionAutoloadMiddleware, SessionMiddleware

from {{cookiecutter.project_name}}.config.database import async_session
from {{cookiecutter.project_name}}.config.settings import settings
from {{cookiecutter.project_name}}.metrics import MetricsMiddleware
from {{cookiecutter.project_name}}.models.users import User

user_loader = UserLoader(user_model_class=User)

middleware = [
    Middleware(MetricsMiddleware, exclude=["/metrics", "/health", "/version"]),
    Middleware(SentryAsgiMiddleware),
    Middleware(TrustedHostMiddleware, allowed_hosts=settings.security.trusted_hosts),
    Middleware(RequestLimitMiddleware, max_body_size=128 * 1024**2),
    Middleware(DbSessionMiddleware, async_session=async_session),
    Middleware(
        LocaleMiddleware, locales=settings.localization.languages, default_locale=settings.localization.language
    ),
    Middleware(TimezoneMiddleware, fallback=settings.localization.timezone),
    Middleware(
        SessionMiddleware,
        rolling=True,
        cookie_https_only=settings.environment != "test",
        lifetime=settings.session.lifetime,
        cookie_path="/",
        store=CookieStore(secret_key=settings.secret_key),
    ),
    Middleware(SessionAutoloadMiddleware),
    Middleware(
        AuthenticationMiddleware,
        backend=ChoiceBackend(
            [
                SessionBackend(user_loader),
                RememberMeBackend(user_loader, secret_key=settings.secret_key),
            ]
        ),
    ),
]
