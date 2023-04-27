import datetime

from kupala.authentication import forget_me, login, logout, remember_me
from kupala.contrib.sqlalchemy.dependencies import DbSession
from kupala.requests import Request
from kupala.responses import redirect_to_path
from kupala.routing import Routes
from starlette.responses import RedirectResponse, Response
from starlette_babel import gettext_lazy as _
from starlette_flash import flash

from {{cookiecutter.project_name}}.accounts.authentication.exceptions import AuthenticationError, InvalidCredentials, NoSuchUserError
from {{cookiecutter.project_name}}.accounts.authentication.forms import LoginForm
from {{cookiecutter.project_name}}.accounts.authentication.user_checks import UserCheck, reject_disabled_users
from {{cookiecutter.project_name}}.accounts.rate_limit import RateLimited, with_rate_limit
from {{cookiecutter.project_name}}.config.dependencies import Settings
from {{cookiecutter.project_name}}.config.templating import templates
from {{cookiecutter.project_name}}.models.users import User

routes = Routes()
user_checks: list[UserCheck] = [
    reject_disabled_users,
]


@routes.get_or_post("/login", name="login")
async def login_view(request: Request, session: DbSession, settings: Settings) -> Response:
    if request.user.is_authenticated:
        if success_message := request.session.pop("success_message", ""):
            flash(request).success(success_message)

        redirect_url = request.url_for(settings.security.post_login_redirect_path)
        if success_url := request.session.pop("success_url", ""):
            redirect_url = success_url
        return RedirectResponse(redirect_url, 302)

    form = await LoginForm.from_request(request)
    if await form.validate_on_submit(request):
        assert request.client
        rate_limit_key = f"{form.email.data}:{request.client.host}".lower()
        try:
            async with with_rate_limit(
                key=rate_limit_key,
                message=_("Too many failed login attempts."),
                namespace="login",
                limit=settings.security.login_rate_limit,
            ) as limiter:
                # test if the user is a valid user
                user = await User.get_by_email(session, form.email.data)
                if not user:
                    raise NoSuchUserError(_("Invalid email or password"))

                # test if user supplied valid password
                if not user.check_password(form.password.data):
                    raise InvalidCredentials(_("Invalid email or password."))

                # test if user login is not restricted (eg. accounts disabled).
                for user_check in user_checks:
                    await user_check(request, user)

                # all ok, do log in
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

                response = RedirectResponse(redirect_url, status_code=302)
                if form.remember_me.data:
                    remember_me(
                        response,
                        settings.secret_key,
                        user,
                        datetime.timedelta(seconds=settings.security.remember_me_duration),
                    )

                # reset rate limit counter
                await limiter.reset(rate_limit_key)

                success_message = request.session.pop("success_message", _("Authenticated successfully."))
                flash(request).success(success_message)
                return response
        except (RateLimited, AuthenticationError) as ex:
            flash(request).error(str(ex))
            return redirect_to_path(
                request,
                path_name="login",
                headers={
                    "x-error-code": getattr(ex, "error_code", ""),
                },
            )

    return templates.TemplateResponse(
        request,
        "accounts/authentication/login.html",
        {
            "page_title": _("Welcome back"),
            "form": form,
        },
    )


@routes.post("/logout", name="logout")
async def logout_view(request: Request) -> Response:
    await logout(request)

    flash(request).success(_("You have been signed out."))
    response = redirect_to_path(request, path_name="login")
    return forget_me(response)
