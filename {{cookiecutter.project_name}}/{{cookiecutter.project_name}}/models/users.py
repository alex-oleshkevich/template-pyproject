from __future__ import annotations

import datetime
import hashlib

import sqlalchemy as sa
from kupala.contrib.sqlalchemy.query import query
from kupala.contrib.sqlalchemy.types import AutoCreatedAt, IntPk
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from starlette.authentication import BaseUser
from starlette_babel import timezone

from {{cookiecutter.project_name}}.accounts.passwords import check_password_hash, generate_password_hash
from {{cookiecutter.project_name}}.config.database import Base


class User(Base, BaseUser):
    __tablename__ = "users"

    id: Mapped[IntPk]
    first_name: Mapped[str] = mapped_column(sa.String(512), default="", server_default="")
    last_name: Mapped[str] = mapped_column(sa.String(512), default="", server_default="")
    email: Mapped[str] = mapped_column(sa.String(512), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(sa.String(512), nullable=False)
    joined_at: Mapped[AutoCreatedAt]
    timezone: Mapped[str | None]
    language: Mapped[str | None]
    active: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=True, server_default="t")
    photo: Mapped[str | None] = mapped_column(sa.String(512))
    email_confirmed_at: Mapped[datetime.datetime | None] = mapped_column(sa.DateTime(True))

    @property
    def identity(self) -> str:
        return str(self.id)

    @property
    def display_name(self) -> str:
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email

    @property
    def avatar(self) -> str:
        email_hash = hashlib.md5(self.email.encode()).hexdigest()  # nosec
        return f"https://www.gravatar.com/avatar/{email_hash}?s=128&d=identicon"

    def __str__(self) -> str:
        return self.display_name

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def is_confirmed(self) -> bool:
        return self.email_confirmed_at is not None

    def set_password(self, plain_password: str) -> None:
        self.password = generate_password_hash(plain_password)

    def check_password(self, plain_password: str) -> bool:
        return check_password_hash(plain_password, self.password)

    def confirm_email(self) -> None:
        self.email_confirmed_at = timezone.now()

    @classmethod
    async def get_by_email(cls, session: AsyncSession, email: str) -> User | None:
        return await query(session).one_or_none(sa.select(cls).where(sa.func.lower(User.email) == email.lower()))

    @classmethod
    def new(
        cls,
        *,
        email: str,
        first_name: str = "",
        last_name: str = "",
        active: bool = True,
        hashed_password: str = "",
        plain_password: str = "",
    ) -> User:
        assert plain_password or hashed_password
        return User(
            email=email,
            active=active,
            password=hashed_password or generate_password_hash(plain_password),
            first_name=first_name,
            last_name=last_name,
        )

    @classmethod
    async def create_user(cls, session: AsyncSession, *, email: str, plain_password: str) -> User:
        user = cls.new(email=email, plain_password=plain_password)
        session.add(user)
        await session.flush([user])
        return user
