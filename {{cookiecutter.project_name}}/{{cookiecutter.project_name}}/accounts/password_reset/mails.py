from starlette_babel import gettext_lazy as _

from {{cookiecutter.project_name}}.config.mails import send_templated_mail
from {{cookiecutter.project_name}}.models.users import User


async def send_password_reset_link(user: User, link: str) -> None:
    await send_templated_mail(
        to=user.email,
        subject=_("Your password reset link."),
        html_template="accounts/password_reset/mail_reset_password.html",
        context={"user": user, "link": link},
    )


async def send_password_changed_mail(user: User) -> None:
    await send_templated_mail(
        to=user.email,
        subject=_("Your password has been changed."),
        html_template="accounts/password_reset/mail_password_changed.html",
        context={"user": user},
    )
