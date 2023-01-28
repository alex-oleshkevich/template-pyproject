import dataclasses
from email.message import Message

import pytest
from itsdangerous import TimestampSigner
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from {{cookiecutter.project_name}}.config.settings import Settings
from {{cookiecutter.project_name}}.models.users import User


def test_password_reset_page_accessible(client: TestClient, mailbox: list[Message]) -> None:
    response = client.get("/reset-password")
    assert response.status_code == 200


def test_reset_page_rate_limited(client: TestClient, user: User, mailbox: list[Message], settings: Settings) -> None:
    settings.security.password_reset_rate_limit = "1/minute"

    client.post("/reset-password", data={"email": "invali@email.tld"})
    response = client.post("/reset-password", data={"email": "invali@email.tld"}, allow_redirects=False)
    assert response.headers["x-error-code"] == "rate_limited"


def test_requests_password_reset_for_invalid_account(client: TestClient, user: User, mailbox: list[Message]) -> None:
    response = client.post("/reset-password", data={"email": "invali@email.tld"})
    assert response.status_code == 200
    assert not mailbox


def test_requests_password_reset(client: TestClient, user: User, mailbox: list[Message]) -> None:
    response = client.post("/reset-password", data={"email": user.email})
    assert response.status_code == 200
    assert len(mailbox) == 1


@dataclasses.dataclass
class PasswordResetToken:
    user: User
    token: str


@pytest.fixture
def password_reset_token(user: User, settings: Settings) -> PasswordResetToken:
    signer = TimestampSigner(secret_key=settings.secret_key)
    return PasswordResetToken(user=user, token=signer.sign(user.email.encode()).decode())


def test_change_password_page_with_valid_token(client: TestClient, password_reset_token: PasswordResetToken) -> None:
    response = client.get(f"/change-password/{password_reset_token.token}", allow_redirects=False)
    assert response.status_code == 200


def test_change_password_page_with_invalid_token(client: TestClient, user: User) -> None:
    response = client.get("/change-password/invalid-token", allow_redirects=False)
    assert response.status_code == 302
    assert response.headers["x-error"] == "invalid_token"


def test_change_password_page_validates_password(client: TestClient, password_reset_token: PasswordResetToken) -> None:
    response = client.post(
        f"/change-password/{password_reset_token.token}",
        data={
            "password": "one",
            "password_confirmation": "two",
        },
        allow_redirects=False,
    )
    assert response.status_code == 200
    assert "Passwords did not match" in response.text


def test_change_password_page_changes_password(
    client: TestClient,
    password_reset_token: PasswordResetToken,
    mailbox: list[Message],
    sync_session: Session,
) -> None:
    response = client.post(
        f"/change-password/{password_reset_token.token}",
        data={
            "password": "someALSKNDI&#@*34",
            "password_confirmation": "someALSKNDI&#@*34",
        },
        allow_redirects=False,
    )

    sync_session.refresh(password_reset_token.user)
    assert password_reset_token.user.check_password("someALSKNDI&#@*34")
    assert response.status_code == 302
    assert response.headers["location"] == "http://testserver/home"
