from itsdangerous import BadSignature, TimestampSigner
from kupala.authentication import login
from kupala.contrib.sqlalchemy.dependencies import DbSession
from kupala.injectables import FromPath
from kupala.requests import Request
from kupala.responses import redirect_to_path
from kupala.routing import Routes
from starlette.background import BackgroundTask
from starlette.responses import Response
from starlette_babel import gettext_lazy as _
from starlette_flash import flash

from {{cookiecutter.project_name}}.accounts.password_reset.forms import ChangePasswordForm, ForgotPasswordForm
from {{cookiecutter.project_name}}.accounts.password_reset.mails import send_password_changed_mail, send_password_reset_link
from {{cookiecutter.project_name}}.base.rate_limit import RateLimited, with_rate_limit
from {{cookiecutter.project_name}}.config.dependencies import Settings
from {{cookiecutter.project_name}}.config.templating import templates
from {{cookiecutter.project_name}}.models.users import User

routes = Routes()


class PasswordResetError(Exception):
    ...


@routes.get_or_post("/reset-password", name="forgot_password")
async def forgot_password_view(request: Request, session: DbSession, settings: Settings) -> Response:
    form = await ForgotPasswordForm.from_request(request)
    if await form.validate_on_submit(request):
        assert request.client
        limiter_key = f"{form.email.data}:{request.client.host}"
        try:
            async with with_rate_limit(
                key=limiter_key,
                namespace="password-recovery",
                message=_("Too many attempts. Please try later."),
                limit=settings.security.password_reset_rate_limit,
            ):
                background_task: BackgroundTask | None = None
                if user := await User.get_by_email(session, form.email.data):
                    serializer = TimestampSigner(secret_key=settings.secret_key)
                    token = serializer.sign(user.email.encode()).decode()
                    link = request.url_for("change_password", token=token)
                    background_task = BackgroundTask(send_password_reset_link, user, str(link))

            flash(request).success(_("Link is sent to your email."))
            return redirect_to_path(request, "forgot_password", background=background_task)
        except RateLimited as ex:
            flash(request).error(str(ex))
            return redirect_to_path(
                request,
                "forgot_password",
                headers={
                    "x-error-code": getattr(ex, "error_code", ""),
                },
            )

    return templates.TemplateResponse(
        request,
        "accounts/password_reset/forgot_password.html",
        {"form": form, "page_title": _("Forgot your password?")},
    )


@routes.get_or_post("/change-password/{token}", name="change_password")
async def new_password_view(request: Request, token: FromPath[str], session: DbSession, settings: Settings) -> Response:
    try:
        signer = TimestampSigner(settings.secret_key)
        email = signer.unsign(token, max_age=settings.security.password_reset_token_lifetime).decode()
        user: User | None = await User.get_by_email(session, email)
        if not user:
            raise PasswordResetError("User does not exists.")
    except (PasswordResetError, BadSignature):
        flash(request).error(_("Password recovery request expired or invalid. Please try again."))
        return redirect_to_path(request, "forgot_password", headers={"x-error": "invalid_token"})

    form = await ChangePasswordForm.from_request(request)
    if await form.validate_on_submit(request):
        user.set_password(form.password.data)
        await session.commit()
        await login(request, user)

        flash(request).success(_("Your password has been changed."))
        task = BackgroundTask(send_password_changed_mail, user)
        return redirect_to_path(request, path_name="home-redirect", background=task)

    return templates.TemplateResponse(
        request,
        "accounts/password_reset/change_password.html",
        {"form": form, "page_title": _("Set new password")},
    )
