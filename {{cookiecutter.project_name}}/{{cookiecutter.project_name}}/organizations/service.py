import sqlalchemy as sa
from kupala.collection import Collection
from kupala.contrib.sqlalchemy.query import query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from {{cookiecutter.project_name}}.models.organizations import Member, Organization


def get_current_organization(request: Request) -> Organization | None:
    try:
        return request.state.organization
    except AttributeError:
        return None


def select_organization(request: Request, organization_id: str | int) -> None:
    request.session["organization_id"] = organization_id


async def get_user_organizations(session: AsyncSession, user_id: int) -> Collection[Organization]:
    stmt = (
        sa.select(Organization)
        .distinct()
        .outerjoin(Member)
        .where(sa.sql.or_(Organization.owner_id == user_id, Member.user_id == user_id))
        .order_by(Organization.name)
    )
    return await query(session).all(stmt)


async def create_organization(
    session: AsyncSession,
    owner_id: int,
    name: str,
    logo: str | None = None,
    timezone: str | None = None,
    support_email: str | None = None,
    support_phone: str | None = None,
) -> Organization:
    organization = Organization(
        name=name,
        logo=logo,
        owner_id=owner_id,
        timezone=timezone,
        support_email=support_email,
        support_phone=support_phone,
    )
    member = Member(organization=organization, user_id=owner_id, permissions=["admin", "owner"])
    session.add(organization)
    session.add(member)

    await session.commit()
    return organization
