from {{cookiecutter.project_name}}.config.mails import send_templated_mail
from {{cookiecutter.project_name}}.models.users import User


async def send_confirm_email_mail(user: User, link: str) -> None:
    await send_templated_mail(
        to=user.email,
        subject="Please confirm your email address",
        html_template="accounts/registration/mail_confirm_email.html",
        context={"user": user, "link": link},
    )
