import dataclasses
from email.message import Message

import pytest
from faker import Faker
from itsdangerous import Signer
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from {{cookiecutter.project_name}}.config.settings import Settings
from {{cookiecutter.project_name}}.models.users import User


@pytest.fixture
def random_email() -> str:
    return Faker().email()


def test_page_accessible(client: TestClient) -> None:
    assert client.get("/register").status_code == 200


def test_registration_validates_duplicate_emails(client: TestClient, user: User) -> None:
    response = client.post(
        "/register",
        data={
            "first_name": "Some",
            "last_name": "User",
            "email": user.email,
            "password": "MASDL @o*#2!SDsd",
            "password_confirmation": "MASDL @o*#2!SDsd",
            "terms": True,
        },
        allow_redirects=False,
    )
    assert response.status_code == 200
    assert "This address is not available" in response.text


def test_registration_creates_account(client: TestClient, random_email: str, mailbox: list[Message]) -> None:
    response = client.post(
        "/register",
        data={
            "first_name": "Some",
            "last_name": "User",
            "email": random_email,
            "password": "MASDL @o*#2!SDsd",
            "terms": True,
        },
        allow_redirects=False,
    )
    assert response.status_code == 302
    assert response.headers["location"] == "http://testserver/home"
    assert mailbox


def test_registration_rate_limited(client: TestClient, settings: Settings) -> None:
    old_value = settings.security.registration_rate_limit
    settings.security.registration_rate_limit = "1/minute"

    faker = Faker()

    client.post(
        "/register",
        data={
            "first_name": "Some",
            "last_name": "User",
            "email": faker.email(),
            "password": "MASDL @o*#2!SDsd",
            "terms": True,
        },
        allow_redirects=False,
    )
    response = client.post(
        "/register",
        data={
            "first_name": "Some",
            "last_name": "User",
            "email": faker.email(),
            "password": "MASDL @o*#2!SDsd",
            "terms": True,
        },
        allow_redirects=False,
    )
    assert response.headers["x-error-code"] == "rate_limited"
    settings.security.registration_rate_limit = old_value


@dataclasses.dataclass
class ConfirmationToken:
    user: User
    token: str


@pytest.fixture()
def confirmation_token(user: User, settings: Settings) -> ConfirmationToken:
    token = Signer(secret_key=settings.secret_key).sign(user.email).decode()
    return ConfirmationToken(user=user, token=token)


def test_email_confirmation_confirms_token(
    client: TestClient, confirmation_token: ConfirmationToken, sync_session: Session
) -> None:
    resource = client.get(f"/register/confirm/{confirmation_token.token}", allow_redirects=False)
    assert resource.status_code == 302
    assert resource.headers["location"] == "http://testserver/home"

    sync_session.refresh(confirmation_token.user)
    assert confirmation_token.user.is_confirmed


def test_email_confirmation_rejects_invalid_tokens(client: TestClient) -> None:
    resource = client.get("/register/confirm/invalid-token", allow_redirects=False)
    assert resource.status_code == 302
    assert resource.headers["x-error-code"] == "invalid_token"
