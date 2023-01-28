from unittest import mock

import sqlalchemy as sa
from faker import Faker
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from {{cookiecutter.project_name}}.models.users import User


def get_payload(email: str) -> dict:
    return {
        "access_token": "",
        "expires_in": 3599,
        "scope": "https://www.googleapis.com/auth/userinfo.profile",
        "token_type": "Bearer",
        "id_token": "",
        "expires_at": 1671817516,
        "userinfo": {
            "iss": "https://accounts.google.com",
            "azp": "487962909894-j24dnl4t1i8rq7jfl3mdhj2qd1b8imvp.apps.googleusercontent.com",
            "aud": "487962909894-j24dnl4t1i8rq7jfl3mdhj2qd1b8imvp.apps.googleusercontent.com",
            "sub": "110027698617019101337",
            "email": email,
            "email_verified": True,
            "at_hash": "2n0IE8Xl3eKUjliLW5I0xg",
            "nonce": "9HBf4drYREunovrn5gkz",
            "name": "Alex Oleshkevich",
            "picture": "https://lh3.googleusercontent.com/a/AEdFTp5b6cZd3JaUQ9MlqtZ4IC14d0GQOhuULxlgQSJp0do=s96-c",
            "given_name": "Alex",
            "family_name": "Oleshkevich",
            "locale": "en",
            "iat": 1671813917,
            "exp": 1671817517,
        },
    }


def test_page_accessible(client: TestClient) -> None:
    response = client.get("/social/google", allow_redirects=False)
    assert response.status_code == 302
    assert "accounts.google.com" in response.headers["location"]


def test_login_existing_user(client: TestClient, user: User) -> None:
    client.cookies.clear()

    payload = get_payload(user.email)

    with mock.patch("{{cookiecutter.project_name}}.accounts.social.views.oauth.google.authorize_access_token", return_value=payload):
        response = client.get("/social/google/callback", allow_redirects=False)
        assert response.status_code == 302
        assert response.headers["location"] == "http://testserver/home"


def test_login_new_user(client: TestClient, faker: Faker, sync_session: Session) -> None:
    client.cookies.clear()

    email = faker.email()
    payload = get_payload(email)

    with mock.patch("{{cookiecutter.project_name}}.accounts.social.views.oauth.google.authorize_access_token", return_value=payload):
        response = client.get("/social/google/callback", allow_redirects=False)
        assert response.status_code == 302
        assert response.headers["location"] == "http://testserver/home"

    assert sync_session.scalar(sa.select(User).where(User.email == email))
