import secrets
import typing

from authlib.integrations.starlette_client import OAuth, StarletteOAuth1App
from authlib.oauth2.rfc6749 import OAuth2Token
from kupala.authentication import login
from kupala.contrib.sqlalchemy.dependencies import DbSession
from kupala.responses import redirect, redirect_to_path
from kupala.routing import Routes
from starlette.responses import Response
from starlette_babel import gettext_lazy as _

from {{cookiecutter.project_name}}.base.http import HttpRequest
from {{cookiecutter.project_name}}.config.dependencies import Settings
from {{cookiecutter.project_name}}.config.settings import get_settings
from {{cookiecutter.project_name}}.models.users import User

routes = Routes()
settings = get_settings()
oauth = OAuth()
oauth.register(
    "google",
    client_id=settings.social.google_client_id,
    client_secret=settings.social.google_client_secret,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile", "prompt": "select_account"},
)
GoogleClient = typing.Annotated[StarletteOAuth1App, lambda: oauth.create_client("google")]


@routes.get("/social/google", name="social_login.request.google")
async def login_via_google(request: HttpRequest, google_client: GoogleClient) -> Response:
    redirect_url = request.url_for("social_login.callback.google")
    return await google_client.authorize_redirect(request, redirect_url)


@routes.get("/social/google/callback", name="social_login.callback.google")
async def login_via_google_callback(
    request: HttpRequest, google_client: GoogleClient, session: DbSession, settings: Settings
) -> Response:
    token: OAuth2Token = await google_client.authorize_access_token(request)
    user_info = token.get("userinfo")
    if not user_info:
        request.flash.error(_("Authentication error."))
        return redirect_to_path(request, "login")

    email = user_info["email"]
    first_name = user_info["given_name"]
    last_name = user_info["family_name"]
    avatar = user_info["picture"]
    locale = user_info["locale"]

    user = await User.get_by_email(session, email)
    if not user:
        user = User(email=email, first_name=first_name, last_name=last_name, photo=avatar, language=locale)
        user.set_password(secrets.token_hex(32))
        user.confirm_email()
        session.add(user)
        await session.commit()

    await login(request, user)
    redirect_url = request.url_for(settings.security.post_login_redirect_path)
    if (
        (requested_next := request.query_params.get("next"))
        and request.url.hostname
        and request.url.hostname in requested_next
    ):
        redirect_url = requested_next

    if success_url := request.session.pop("success_url", ""):
        redirect_url = success_url

    success_message = request.session.pop("success_message", _("Authenticated successfully."))
    request.flash.success(success_message)
    return redirect(redirect_url)
