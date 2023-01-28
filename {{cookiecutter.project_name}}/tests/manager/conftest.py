from starlette.testclient import TestClient

from {{cookiecutter.project_name}}.models.organizations import Member
from tests.conftest import force_login


def test_manage_area_accessible_to_authenticated_only(client: TestClient) -> None:
    response = client.get("/manage/dashboard", allow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "/login"


def test_manage_area_accessible_by_members_only(client: TestClient, member: Member) -> None:
    force_login(client, member.user)
    response = client.get(
        "/manage/dashboard",
        allow_redirects=False,
        cookies={"organization_id": str(member.organization_id)},
    )
    assert response.status_code == 200
