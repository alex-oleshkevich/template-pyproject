import logging

import sqlalchemy as sa
from itsdangerous import BadSignature, Signer
from kupala.contrib.sqlalchemy.dependencies import DbSession
from kupala.contrib.sqlalchemy.query import query
from kupala.exceptions import PageNotFound
from kupala.injectables import FromPath
from kupala.responses import redirect_to_path
from kupala.routing import Routes
from sqlalchemy.orm import joinedload
from starlette.responses import Response
from starlette_babel import gettext_lazy as _

from {{cookiecutter.project_name}}.base.http import HttpRequest
from {{cookiecutter.project_name}}.config.dependencies import Settings
from {{cookiecutter.project_name}}.models.organizations import Member, MemberInvitation
from {{cookiecutter.project_name}}.models.users import User
from {{cookiecutter.project_name}}.organizations.service import select_organization

routes = Routes()


async def _fetch_invitation(session: DbSession, invitation_token: FromPath[str]) -> MemberInvitation:
    return await query(session).one_or_raise(
        sa.select(MemberInvitation)
        .options(joinedload(MemberInvitation.organization))
        .where(MemberInvitation.token == invitation_token),
        PageNotFound("Invitation not found."),
    )


@routes("/join-organization/{token:str}", name="onboarding.accept_organization_invitation")
async def accept_member_invitation_view(
    request: HttpRequest,
    session: DbSession,
    settings: Settings,
    token: FromPath[str],
) -> Response:
    invitation = await _fetch_invitation(session, token)
    signer = Signer(settings.secret_key)
    request.session["organization_invitation_token"] = signer.sign(invitation.token).decode()
    request.session["success_url"] = str(request.url_for("onboarding.finalize_member_signup"))
    request.session["form_prefill"] = {"email": invitation.email}

    if await User.get_by_email(session, invitation.email):
        return redirect_to_path(request, "login")

    return redirect_to_path(request, "register")


@routes("/member/finalize", name="onboarding.finalize_member_signup")
async def finalize_member_signup_view(request: HttpRequest, session: DbSession, settings: Settings) -> Response:
    try:
        signer = Signer(settings.secret_key)
        invitation_token = signer.unsign(request.session.pop("organization_invitation_token", "")).decode()
        invitation = await _fetch_invitation(session, invitation_token)

        member: Member | None = await query(session).one_or_none(
            sa.select(Member)
            .options(joinedload(Member.user))
            .join(Member.user)
            .where(
                sa.func.lower(User.email) == invitation.email.lower(),
                Member.organization_id == invitation.organization_id,
            )
        )
        if not member:
            member = Member(user=request.user, organization=invitation.organization, permissions=invitation.permissions)
            session.add(member)

        await invitation.accept(session)
        await session.commit()

        select_organization(request, invitation.organization_id)
        request.flash.success(_("Welcome to {organization}.").format(organization=invitation.organization))
        return redirect_to_path(request, "manage.dashboard")
    except BadSignature as ex:
        logging.exception(ex)
        request.flash.error(_("Invalid request."))
        return redirect_to_path(request, "register")
