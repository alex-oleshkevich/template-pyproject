from email.message import EmailMessage

import faker
from starlette.testclient import TestClient

from {{cookiecutter.project_name}}.models.organizations import Member
from tests.conftest import force_login, force_organization
from tests.factories import MembershipInvitationFactory


def test_teams(client: TestClient, member: Member) -> None:
    force_login(client, member.user)
    force_organization(client, member.organization)

    response = client.get("/manage/team")
    assert response.status_code == 200
    assert "Team" in response.text
    assert member.display_name in response.text

    response = client.get("/manage/team", headers={"hx-target": "datatable"})
    assert response.status_code == 200
    assert "Team" not in response.text
    assert member.display_name in response.text


def test_delete_member(client: TestClient, member: Member) -> None:
    force_login(client, member.user)
    force_organization(client, member.organization)

    response = client.delete(f"/manage/team/{member.id}/delete")
    assert response.status_code == 204
    assert "refresh_datatable" in response.headers["hx-trigger"]
    assert "deleted" in response.headers["hx-trigger"]


def test_invite_member(client: TestClient, member: Member, mailbox: list[EmailMessage]) -> None:
    force_login(client, member.user)
    force_organization(client, member.organization)

    response = client.get("/manage/team/invite")
    assert response.status_code == 200
    assert "Invite team member" in response.text

    response = client.post("/manage/team/invite", data={"email": faker.Faker().email(), "message": "MEMBERMESSAGE"})
    assert response.status_code == 204
    assert "modals.close" in response.headers["hx-trigger"]
    assert "refresh_team_invitations" in response.headers["hx-trigger"]
    assert "sent" in response.headers["hx-trigger"]
    assert mailbox
    assert "MEMBERMESSAGE" in mailbox[0].as_string()


def test_team_invites(client: TestClient, member: Member) -> None:
    force_login(client, member.user)
    force_organization(client, member.organization)
    email = faker.Faker().email()
    MembershipInvitationFactory.create(
        organization=member.organization, email=email, token="MEMBERTOKEN1", invitor=member
    )

    response = client.get("/manage/teams/invites")
    assert response.status_code == 200
    assert "Sent invitations" in response.text
    assert email in response.text


def test_delete_team_invite(client: TestClient, member: Member) -> None:
    force_login(client, member.user)
    force_organization(client, member.organization)
    email = faker.Faker().email()
    invitation = MembershipInvitationFactory.create(
        organization=member.organization, email=email, token="MEMBERTOKEN2", invitor=member
    )

    response = client.delete(f"/manage/teams/invites/{invitation.id}/delete")
    assert response.status_code == 204
    assert "refresh_team_invitations" in response.headers["hx-trigger"]
    assert "deleted" in response.headers["hx-trigger"]
