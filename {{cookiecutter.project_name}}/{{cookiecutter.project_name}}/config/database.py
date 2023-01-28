import typing

import sqlalchemy as sa
from kupala.contrib.sqlalchemy import SQLAlchemy, query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, mapped_column

from {{cookiecutter.project_name}}.config.settings import settings

db = SQLAlchemy(
    database_url=settings.database.database_url,
    engine_options=dict(
        echo=settings.database.echo,
        pool_size=settings.database.pool_size,
        pool_timeout=settings.database.pool_timeout,
        max_overflow=settings.database.pool_max_overflow,
    ),
)
async_session = db.async_session_factory
metadata = db.metadata

UserFk = typing.Annotated[int, mapped_column(sa.ForeignKey("users.id"), nullable=False)]
OrganizationFk = typing.Annotated[int, mapped_column(sa.ForeignKey("organizations.id"), nullable=False)]
get_async_session = async_session


class Base(DeclarativeBase):
    __tablename__: str
    metadata = metadata

    @classmethod
    async def get(
        cls, session: AsyncSession, pk: typing.Any, pk_column: str = "id", options: list | None = None
    ) -> typing.Any:
        stmt = sa.select(cls).where(getattr(cls, pk_column) == pk)
        if options:
            stmt = stmt.options(options)
        return await query(session).one(stmt)

    @classmethod
    async def get_or_none(cls, session: AsyncSession, pk: typing.Any, pk_column: str = "id") -> typing.Any | None:
        return await query(session).one_or_none(sa.select(cls).where(getattr(cls, pk_column) == pk))

    @classmethod
    async def get_or_raise(
        cls, session: AsyncSession, pk: typing.Any, exc: Exception, pk_column: str = "id"
    ) -> typing.Any | None:
        return await query(session).one_or_raise(sa.select(cls).where(getattr(cls, pk_column) == pk), exc)
