from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from {{cookiecutter.project_name}}.models.users import User
from tests.conftest import force_login


def test_profile_not_accessible_for_unauthenticated(client: TestClient) -> None:
    response = client.get("/profile", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["location"]


def test_profile_accessible_for_authenticated(client: TestClient, user: User) -> None:
    force_login(client, user)
    response = client.get("/profile", follow_redirects=False)
    assert response.status_code == 200


def test_updates_user_info(client: TestClient, user: User) -> None:
    force_login(client, user)
    response = client.post(
        "/profile",
        data={"first_name": "user1", "last_name": "user2", "_profile": "1"},
        headers={"referer": "http://testserver/profile"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert response.headers["location"] == "http://testserver/profile"


def test_password_change_fails_for_invalid_current_password(client: TestClient, user: User) -> None:
    force_login(client, user)
    response = client.post(
        "/profile",
        data={
            "current_password": "invalid",
            "password": "password2",
            "confirm_password": "password2",
            "_password": "1",
        },
        headers={"referer": "http://testserver/profile"},
        follow_redirects=False,
    )
    assert response.status_code == 200
    assert "Invalid current password" in response.text


def test_password_change_fails_for_password_mismatch(client: TestClient, user: User) -> None:
    force_login(client, user)
    response = client.post(
        "/profile",
        data={
            "current_password": "password",
            "password": "password2",
            "confirm_password": "password3",
            "_password": "1",
        },
        headers={"referer": "http://testserver/profile"},
        follow_redirects=False,
    )
    assert response.status_code == 200
    assert "Field must be equal to password" in response.text


def test_password_changes_password(client: TestClient, user: User, sync_session: Session) -> None:
    force_login(client, user)
    response = client.post(
        "/profile",
        data={
            "current_password": "password",
            "password": "password2",
            "confirm_password": "password2",
            "_password": "1",
        },
        follow_redirects=False,
    )
    assert response.status_code == 302

    sync_session.refresh(user)
    assert user.check_password("password2")
