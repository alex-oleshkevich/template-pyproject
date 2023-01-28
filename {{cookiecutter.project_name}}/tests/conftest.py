import asyncio
import typing
from asyncio import get_event_loop

import pytest
import sqlalchemy as sa
from mailers import InMemoryTransport, Mailer
from mailers.pytest_plugin import Mailbox
from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from starlette.applications import Starlette
from starlette.testclient import TestClient
from starlette_babel import switch_locale, switch_timezone

from {{cookiecutter.project_name}}.config.database import metadata
from {{cookiecutter.project_name}}.config.mails import get_mailer
from {{cookiecutter.project_name}}.config.settings import Settings, get_settings
from {{cookiecutter.project_name}}.main import create_app
from {{cookiecutter.project_name}}.models.organizations import Member, Organization
from {{cookiecutter.project_name}}.models.users import User
from {{cookiecutter.project_name}}.subscriptions.models import Plan
from {{cookiecutter.project_name}}.subscriptions.packages import FREE_PACKAGE
from tests.database import Session
from tests.factories import MemberFactory, OrganizationFactory, UserFactory


@pytest.fixture(scope="session")
def event_loop() -> typing.Generator[asyncio.AbstractEventLoop, None, None]:
    yield get_event_loop()


@pytest.fixture(scope="session")
def settings() -> Settings:
    return get_settings()


@pytest.fixture(scope="session")
def app(settings: Settings) -> Starlette:
    return create_app(settings)


@pytest.fixture(scope="session")
def client(app: Starlette) -> typing.Generator[TestClient, None, None]:
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function", autouse=True)
def logout_client(client: TestClient) -> None:
    client.cookies.clear()


def force_login(client: TestClient, user: User) -> None:
    client.post("/login", data={"email": user.email, "password": "password"})


def force_organization(client: TestClient, organization: int | Organization) -> None:
    organization_id = str(organization.id) if isinstance(organization, Organization) else str(organization)
    client.cookies.setdefault("organization_id", organization_id)


@pytest.fixture()
def auth_client(app: Starlette) -> typing.Generator[TestClient, None, None]:
    with TestClient(app) as client:
        client.cookies.clear()
        yield client


@pytest.fixture(scope="session", autouse=True)
def force_locale() -> typing.Generator[None, None, None]:
    with switch_locale("en"), switch_timezone("utc"):
        yield


@pytest.fixture(scope="session")
def run_migrations(settings: Settings) -> typing.Generator[None, None, None]:
    database_url = settings.database.sync_database_url
    if "test" not in database_url:
        # guard against accidental misconfiguration
        raise RuntimeError("Test database must contain test_ or _test addon.")

    engine = create_engine(settings.database.sync_database_url)
    ddl_engine = create_engine(engine.url._replace(database=""), isolation_level="AUTOCOMMIT")
    with ddl_engine.begin() as connection:
        connection.execute(
            sa.text(
                """
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '{database}'
        AND pid <> pg_backend_pid();
        """.format(
                    database=engine.url.database
                )
            )
        )
        connection.execute(sa.text(f"drop database if exists {engine.url.database}"))
        connection.execute(sa.text(f"create database {engine.url.database}"))

    metadata.drop_all(engine)
    metadata.create_all(engine)
    Session.configure(bind=engine)
    yield
    metadata.drop_all(engine)


@pytest.fixture(scope="session", autouse=True)
def base_models(run_migrations: None, sync_session: Session) -> None:
    plan = Plan(name="Free", description="", package=FREE_PACKAGE.name)
    sync_session.add(plan)
    sync_session.commit()
    yield


@pytest.fixture(scope="session")
async def async_engine(settings: Settings) -> typing.AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(settings.database.database_url)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
def sync_engine(settings: Settings) -> typing.Generator[Engine, None, None]:
    engine = create_engine(settings.database.database_url)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
async def db_session(async_engine: AsyncEngine) -> typing.AsyncGenerator[AsyncSession, None]:
    factory = async_sessionmaker(async_engine)
    async with factory() as session:
        yield session


@pytest.fixture(autouse=True, scope="session")
def sync_session(run_migrations: None, sync_engine: Engine) -> typing.Generator[Session, None, None]:
    with Session() as session:
        yield session


@pytest.fixture
def mailer() -> Mailer:
    return get_mailer()


@pytest.fixture(scope="function")
def mailbox(mailer: Mailer) -> typing.Generator[Mailbox, None, None]:
    transport = mailer.transport
    assert isinstance(transport, InMemoryTransport)
    transport.mailbox.clear()
    yield transport.mailbox
    transport.mailbox.clear()


@pytest.fixture
async def user(sync_session: Session) -> User:
    return UserFactory()


@pytest.fixture
def organization(sync_session: Session) -> User:
    return OrganizationFactory()


@pytest.fixture()
def member(sync_session: Session, organization: Organization, user: User) -> Member:
    return MemberFactory(organization=organization, user=user, permissions=["member"])
