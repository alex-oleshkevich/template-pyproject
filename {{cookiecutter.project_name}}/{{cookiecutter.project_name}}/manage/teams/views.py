import json
import uuid

from kupala.contrib.sqlalchemy.dependencies import DbSession
from kupala.injectables import FromPath
from kupala.routing import Routes
from starlette.background import BackgroundTask
from starlette.requests import Request
from starlette.responses import Response
from starlette_babel import gettext_lazy as _

from {{cookiecutter.project_name}}.config.dependencies import CurrentOrganization
from {{cookiecutter.project_name}}.config.templating import templates
from {{cookiecutter.project_name}}.manage.depedencies import CurrentMember
from {{cookiecutter.project_name}}.manage.teams.forms import InviteMemberForm
from {{cookiecutter.project_name}}.manage.teams.mails import send_member_invitation
from {{cookiecutter.project_name}}.manage.teams.tables import TeamTable
from {{cookiecutter.project_name}}.models.organizations import MemberInvitation

routes = Routes()


@routes("/team", name="manage.teams")
async def team_view(request: Request, session: DbSession) -> Response:
    table = TeamTable()
    page = await table.paginate(request, session)

    template = "manage/teams/teams.html"
    if request.headers.get("hx-target", "") == "datatable":
        template = "manage/teams/partials/teams_page.html"

    return templates.TemplateResponse(
        request,
        template,
        {
            "page_title": _("Team"),
            "objects": page,
        },
    )


@routes.delete("/team/{member_id:int}/delete", name="manage.teams.delete")
async def delete_member_view(
    request: Request,
    session: DbSession,
    organization: CurrentOrganization,
    member_id: FromPath[int],
) -> Response:
    await organization.delete_member(session, member_id)
    await session.commit()
    return Response(
        status_code=204,
        headers={
            "hx-trigger": json.dumps(
                {
                    "refresh_datatable": "",
                    "toast": {"message": str(_("Entry has been deleted"))},
                }
            )
        },
    )


@routes.get_or_post("/team/invite", name="manage.teams.invite")
async def invite_member_view(
    request: Request,
    session: DbSession,
    member: CurrentMember,
    organization: CurrentOrganization,
) -> Response:
    form = await InviteMemberForm.from_request(
        request,
        context={
            "organization": organization,
            "dbsession": session,
        },
    )
    if await form.validate_on_submit(request):
        token = uuid.uuid4().hex
        invitation = MemberInvitation(
            token=token,
            permissions=["member"],
            email=form.email.data.lower(),
            invitor=member,
            organization_id=request.state.organization.id,
        )
        link = request.url_for("onboarding.accept_organization_invitation", token=token)
        session.add(invitation)
        await session.commit()
        task = BackgroundTask(
            send_member_invitation,
            organization=organization,
            email=form.email.data,
            link=str(link),
            message=form.message.data,
        )

        return Response(
            status_code=204,
            headers={
                "hx-trigger": json.dumps(
                    {
                        "modals.close": "",
                        "refresh_team_invitations": "",
                        "toast": {"message": str(_("Invitation has been sent."))},
                    }
                )
            },
            background=task,
        )

    return templates.TemplateResponse(
        request,
        "manage/teams/modal_invite.html",
        {
            "form": form,
        },
    )


@routes("/teams/invites", name="manage.teams.invites")
async def invites_view(request: Request, session: DbSession, organization: CurrentOrganization) -> Response:
    members = await organization.get_membership_invitations(session)
    return templates.TemplateResponse(
        request,
        "manage/teams/invites.html",
        {
            "objects": members,
        },
    )


@routes.delete("/teams/invites/{invitation_id:int}/delete", name="manage.teams.delete_invitation")
async def delete_invitation_view(
    session: DbSession, organization: CurrentOrganization, invitation_id: FromPath[int]
) -> Response:
    await organization.delete_membership_invitation(session, invitation_id)
    await session.commit()
    return Response(
        status_code=204,
        headers={
            "hx-trigger": json.dumps(
                {"refresh_team_invitations": "", "toast": {"message": str(_("Entry has been deleted"))}}
            )
        },
    )
