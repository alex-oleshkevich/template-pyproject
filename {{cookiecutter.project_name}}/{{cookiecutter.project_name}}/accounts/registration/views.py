from itsdangerous import BadSignature, Signer
from kupala.contrib.sqlalchemy.dependencies import DbSession
from kupala.injectables import FromPath
from kupala.responses import redirect_to_path
from kupala.routing import Routes
from starlette.background import BackgroundTask
from starlette.responses import RedirectResponse, Response
from starlette_babel import gettext_lazy as _
from starlette_flash import flash

from {{cookiecutter.project_name}}.accounts.registration.actions import (
    OnUserRegisteredCallback,
    automatically_login_user,
    create_free_subscription,
    create_user_organization,
)
from {{cookiecutter.project_name}}.accounts.registration.forms import RegisterAsyncForm
from {{cookiecutter.project_name}}.accounts.registration.mails import send_confirm_email_mail
from {{cookiecutter.project_name}}.base.http import HttpRequest
from {{cookiecutter.project_name}}.base.rate_limit import RateLimited, with_rate_limit
from {{cookiecutter.project_name}}.config.dependencies import Settings
from {{cookiecutter.project_name}}.config.templating import templates
from {{cookiecutter.project_name}}.models.users import User

routes = Routes()

post_registration_actions: list[OnUserRegisteredCallback] = [
    automatically_login_user,
    create_free_subscription,
    create_user_organization,
]


class RegistrationError(Exception):
    ...


@routes.get_or_post("/register", name="register")
async def register_view(request: HttpRequest, session: DbSession, settings: Settings) -> Response:
    prefill_data = request.session.get("form_prefill", {})
    form = await RegisterAsyncForm.from_request(request, context={"dbsession": session}, data=prefill_data)

    if await form.validate_on_submit(request):
        assert request.client
        limiter_key = f"{request.client.host}"
        async with session.begin_nested():
            try:
                async with with_rate_limit(
                    key=limiter_key,
                    message=_("Too many attempts. Please try later."),
                    namespace="registration",
                    limit=settings.security.registration_rate_limit,
                ):
                    user = User.new(
                        first_name=form.first_name.data,
                        last_name=form.last_name.data,
                        email=form.email.data,
                        plain_password=form.password.data,
                        active=True,
                    )
                    session.add(user)
                    await session.flush()

                    for action in post_registration_actions:
                        await action(request, user)

                    async def _send_email() -> None:
                        signer = Signer(settings.secret_key)
                        token = signer.sign(user.email).decode()
                        link = request.url_for("register_confirm_email", token=token)
                        await send_confirm_email_mail(user, str(link))

                    task = BackgroundTask(_send_email)

                    redirect_url = request.url_for(settings.security.post_login_redirect_path)
                    if (
                        (requested_next := request.query_params.get("next"))
                        and request.url.hostname
                        and request.url.hostname in requested_next
                    ):
                        redirect_url = requested_next

                    if success_url := request.session.pop("success_url", ""):
                        redirect_url = success_url

                    success_message = request.session.pop("success_message", "")
                    flash(request).success(success_message)

                    return RedirectResponse(redirect_url, status_code=302, background=task)
            except RateLimited as ex:
                flash(request).error(str(ex))
                return redirect_to_path(request, "register", headers={"x-error-code": getattr(ex, "error_code", "")})

    return templates.TemplateResponse(
        request,
        "accounts/registration/register.html",
        {"form": form, "page_title": _("Create account")},
    )


@routes.get("/register/confirm/{token:str}", name="register_confirm_email")
async def confirm_email_view(
    request: HttpRequest, token: FromPath[str], session: DbSession, settings: Settings
) -> Response:
    try:
        signer = Signer(settings.secret_key)
        email = signer.unsign(token).decode()
        user: User | None = await User.get_by_email(session, email)
        if not user:
            raise RegistrationError("User does not exists.")
    except (BadSignature, RegistrationError):
        flash(request).error(_("This confirmation link is invalid."))
        return redirect_to_path(request, "login", headers={"x-error-code": "invalid_token"})

    user.confirm_email()
    await session.commit()

    return redirect_to_path(request, path_name=settings.security.post_login_redirect_path)
