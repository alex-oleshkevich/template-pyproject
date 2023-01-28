import factory
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker

from {{cookiecutter.project_name}}.accounts.passwords import generate_password_hash
from {{cookiecutter.project_name}}.models.organizations import Member, MemberInvitation, Organization
from {{cookiecutter.project_name}}.models.users import User
from {{cookiecutter.project_name}}.subscriptions.models import Plan
from tests.database import Session

faker = Faker()


class BaseFactory(SQLAlchemyModelFactory):
    """Base Factory."""

    class Meta:
        """Factory configuration."""

        abstract = True
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "commit"


class UserFactory(BaseFactory):
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    password = generate_password_hash("password")

    class Meta:
        model = User


class OrganizationFactory(BaseFactory):
    name = factory.Faker("company")
    owner = factory.SubFactory(UserFactory)

    class Meta:
        model = Organization


class MemberFactory(BaseFactory):
    user = factory.SubFactory(UserFactory)
    organization = factory.SubFactory(OrganizationFactory)

    class Meta:
        model = Member


class MembershipInvitationFactory(BaseFactory):
    organization = factory.SubFactory(OrganizationFactory)
    email = factory.Faker("email")
    token = factory.Faker("md5")
    invitor = factory.SubFactory(MemberFactory)

    class Meta:
        model = MemberInvitation


class PlanFactory(BaseFactory):
    name = factory.Faker("lorem")
    description = factory.Faker("lorem")

    class Meta:
        model = Plan
