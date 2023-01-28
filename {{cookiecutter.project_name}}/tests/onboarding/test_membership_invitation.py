import pytest
from starlette.testclient import TestClient

from {{cookiecutter.project_name}}.models.organizations import MemberInvitation, Organization
from tests.factories import MemberFactory, MembershipInvitationFactory, UserFactory


@pytest.fixture
def invitation(organization: Organization) -> MemberInvitation:
    member = MemberFactory.create(organization=organization)
    return MembershipInvitationFactory.create(invitor=member, organization=organization)


def test_invitation_link_for_new_users(client: TestClient, invitation: MemberInvitation) -> None:
    response = client.get(f"/onboarding/join-organization/{invitation.token}", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "http://testserver/register"

    response = client.post(
        "/register",
        data={
            "first_name": "",
            "last_name": "",
            "email": invitation.email,
            "password": "password!",
            "terms": True,
        },
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert response.headers["location"] == "http://testserver/onboarding/member/finalize"

    response = client.get("/onboarding/member/finalize", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "http://testserver/manage/dashboard"


def test_invitation_link_for_app_users(client: TestClient, invitation: MemberInvitation) -> None:
    """When organization has no member but user account exists in the system - create organization member ."""

    UserFactory(email=invitation.email)
    response = client.get(f"/onboarding/join-organization/{invitation.token}", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "http://testserver/login"

    response = client.post("/login", data={"email": invitation.email, "password": "password"}, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "http://testserver/onboarding/member/finalize"

    response = client.get("/onboarding/member/finalize", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "http://testserver/manage/dashboard"


def test_invitation_link_for_existing_members(client: TestClient, invitation: MemberInvitation) -> None:
    """When organization has no member but user account exists in the system - create organization member ."""

    user = UserFactory(email=invitation.email)
    MemberFactory(organization=invitation.organization, user=user)
    response = client.get(f"/onboarding/join-organization/{invitation.token}", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "http://testserver/login"

    response = client.post("/login", data={"email": invitation.email, "password": "password"}, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "http://testserver/onboarding/member/finalize"

    response = client.get("/onboarding/member/finalize", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "http://testserver/manage/dashboard"
