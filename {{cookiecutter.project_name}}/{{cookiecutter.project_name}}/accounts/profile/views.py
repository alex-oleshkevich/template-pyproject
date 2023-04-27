from kupala.authentication import login_required
from kupala.contrib.sqlalchemy.dependencies import DbSession
from kupala.responses import redirect_back
from kupala.routing import Routes
from starlette.requests import Request
from starlette.responses import Response
from starlette_babel import gettext_lazy as _
from starlette_flash import flash

from {{cookiecutter.project_name}}.accounts.password_reset.mails import send_password_changed_mail
from {{cookiecutter.project_name}}.accounts.passwords import check_password_hash
from {{cookiecutter.project_name}}.accounts.profile.forms import ChangePasswordForm, EditProfileForm
from {{cookiecutter.project_name}}.config.templating import templates
from {{cookiecutter.project_name}}.models.users import User

routes = Routes()


@routes.get_or_post("/profile", name="profile", guards=[login_required()])
async def profile_view(request: Request, session: DbSession) -> Response:
    data = await request.form()
    profile_form = EditProfileForm(data, obj=request.user)
    password_form = ChangePasswordForm(data)

    if request.method == 'POST':
        user = await User.get(session, request.user.id)
        data = await request.form()
        if "_profile" in data and profile_form.validate():
            profile_form.populate_obj(user)
            await session.commit()

            flash(request).success(_("Profile has been updated."))
            return redirect_back(request)

        if "_password" in data and password_form.validate():
            if check_password_hash(password_form.current_password.data, user.password):
                user.set_password(password_form.password.data)
                await session.commit()
                await send_password_changed_mail(user)

                flash(request).success(_("Password has been updated."))
                return redirect_back(request)

            password_form.current_password.errors.append(_("Invalid current password."))

    return templates.TemplateResponse(
        request,
        "accounts/profile/profile.html",
        {
            "page_title": _("My profile"),
            "profile_form": profile_form,
            "password_form": password_form,
        },
    )
