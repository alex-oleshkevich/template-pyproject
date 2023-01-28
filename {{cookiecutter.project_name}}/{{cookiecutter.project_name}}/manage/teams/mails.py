from starlette_babel import gettext_lazy as _

from {{cookiecutter.project_name}}.config.mails import send_templated_mail
from {{cookiecutter.project_name}}.models.organizations import Organization


async def send_member_invitation(organization: Organization, email: str, link: str, message: str) -> None:
    await send_templated_mail(
        to=email,
        subject=_("You have been invited to join {organization}.").format(organization=organization),
        html_template="manage/teams/mail_member_invitation.html",
        context={"link": link, "organization": organization, "message": message},
    )
