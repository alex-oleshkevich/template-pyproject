from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from {{cookiecutter.project_name}}.config.settings import Settings
from {{cookiecutter.project_name}}.models.users import User


def test_login_accessible(client: TestClient) -> None:
    response = client.get("/login")
    assert response.status_code == 200


def test_logins_user(client: TestClient, user: User) -> None:
    response = client.post("/login", data={"email": user.email, "password": "password"}, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "http://testserver/home"


def test_remember_me(client: TestClient, user: User) -> None:
    response = client.post("/login", data={"email": user.email, "password": "password"}, follow_redirects=False)
    assert "remember_me" not in response.cookies

    client.cookies.clear()
    response = client.post(
        "/login",
        data={
            "email": user.email,
            "password": "password",
            "remember_me": "y",
        },
        follow_redirects=False,
    )
    assert "remember_me" in response.cookies


def test_login_fails(client: TestClient, user: User) -> None:
    client.cookies.clear()
    response = client.post("/login", data={"email": user.email, "password": "incorrect password"})
    assert response.status_code == 200
    assert "login" in response.url.path


def test_rejects_disabled_accounts(sync_session: Session, client: TestClient, user: User) -> None:
    client.cookies.clear()
    sync_session.merge(user)
    user.active = False
    sync_session.commit()

    response = client.post("/login", data={"email": user.email, "password": "password"}, allow_redirects=False)
    assert response.headers["x-error-code"] == "account_disabled"


def test_login_rate_limit(client: TestClient, user: User, settings: Settings) -> None:
    settings.security.login_rate_limit = "1/minute"

    client.cookies.clear()
    client.post("/login", data={"email": user.email, "password": "incorrect password"})
    response = client.post(
        "/login",
        data={"email": user.email, "password": "incorrect password"},
        allow_redirects=False,
    )
    assert response.headers["x-error-code"] == "rate_limited"


def test_logout(client: TestClient, user: User) -> None:
    client.post("/login", data={"email": user.email, "password": "password"}, follow_redirects=False)
    response = client.post("/logout")
    assert response.status_code == 200
    assert "login" in response.url.path
