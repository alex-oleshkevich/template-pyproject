from __future__ import annotations

import datetime
import typing
import uuid

import sqlalchemy as sa
from kupala.collection import Collection
from kupala.contrib.sqlalchemy.modelmixins import Timestamps
from kupala.contrib.sqlalchemy.query import query
from kupala.contrib.sqlalchemy.types import AutoCreatedAt, AutoUpdatedAt, IntPk, JsonList, ShortString
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from {{cookiecutter.project_name}}.config.database import Base, OrganizationFk, UserFk
from {{cookiecutter.project_name}}.models.users import User

MemberFk = typing.Annotated[int, mapped_column(sa.ForeignKey("organization_members.id"))]


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[IntPk]
    name: Mapped[str] = mapped_column(sa.String(512), nullable=False)
    owner_id: Mapped[UserFk]
    created_at: Mapped[AutoCreatedAt]
    updated_at: Mapped[AutoUpdatedAt]
    deleted_at: Mapped[datetime.datetime | None] = mapped_column(sa.DateTime(True))

    owner: Mapped[User] = relationship(User)
    members: Mapped[Member] = relationship("Member", cascade="all, delete-orphan", back_populates="organization")
    invitations: Mapped[MemberInvitation] = relationship("MemberInvitation", cascade="all, delete-orphan")

    async def get_member(self, session: AsyncSession, user_id: int) -> Member | None:
        return await query(session).one_or_none(
            sa.select(Member).where(Member.organization == self, Member.user_id == user_id)
        )

    async def delete_member(self, session: AsyncSession, member_id: int) -> None:
        member = await query(session).one_or_none(
            sa.select(Member).where(Member.organization == self, Member.id == member_id)
        )
        if member:
            await session.delete(member)
            await session.flush()

    async def get_membership_invitations(self, session: AsyncSession) -> Collection[MemberInvitation]:
        return await query(session).all(sa.select(MemberInvitation).where(MemberInvitation.organization == self))

    async def delete_membership_invitation(self, session: AsyncSession, invitation_id: int) -> None:
        invitation = await query(session).one_or_none(
            sa.select(MemberInvitation).where(
                MemberInvitation.organization == self, MemberInvitation.id == invitation_id
            )
        )
        if invitation:
            await session.delete(invitation)
            await session.flush()

    def __str__(self) -> str:
        return self.name


class Member(Base):
    __tablename__ = "organization_members"
    __table_args__ = (sa.UniqueConstraint("user_id", "organization_id"),)

    id: Mapped[IntPk]
    user_id: Mapped[UserFk]
    organization_id: Mapped[OrganizationFk]
    permissions: Mapped[JsonList]
    created_at: Mapped[AutoCreatedAt]

    organization: Mapped[Organization] = relationship(Organization)
    user: Mapped[User] = relationship(User, foreign_keys="Member.user_id")

    @property
    def avatar(self) -> str:
        return self.user.avatar

    @property
    def display_name(self) -> str:
        return self.user.display_name

    @property
    def email(self) -> str:
        return self.user.email

    def __str__(self) -> str:
        return self.display_name


class MemberInvitation(Base, Timestamps):
    __tablename__ = "organization_invitations"
    __table_args__ = (sa.UniqueConstraint("email", "organization_id"),)

    id: Mapped[IntPk]
    organization_id: Mapped[OrganizationFk]
    email: Mapped[str] = mapped_column(sa.String(256))
    permissions: Mapped[JsonList]
    token: Mapped[ShortString] = mapped_column(default=uuid.uuid4, unique=True)
    invitor_id: Mapped[int | None] = mapped_column(sa.ForeignKey(Member.id))

    invitor: Mapped[Member] = relationship(Member)
    organization: Mapped[Organization] = relationship(Organization, back_populates="invitations")

    async def accept(self, session: AsyncSession) -> None:
        await session.delete(self)
        await session.commit()
