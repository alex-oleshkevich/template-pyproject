from starlette.testclient import TestClient

from {{cookiecutter.project_name}}.models.organizations import Member
from tests.conftest import force_login, force_organization


def test_dashboard(client: TestClient, member: Member) -> None:
    force_login(client, member.user)
    force_organization(client, member.organization)

    response = client.get("/manage/dashboard")
    assert response.status_code == 200
    assert "Dashboard" in response.text
