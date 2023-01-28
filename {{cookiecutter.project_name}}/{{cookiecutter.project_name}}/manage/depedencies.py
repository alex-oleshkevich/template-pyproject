import typing

import sqlalchemy as sa
from kupala.contrib.sqlalchemy import DbQuery
from kupala.exceptions import HTTPException
from starlette.requests import Request

from {{cookiecutter.project_name}}.models.organizations import Member


async def _fetch_current_member(request: Request, query: DbQuery) -> Member:
    return await query.one_or_raise(
        sa.select(Member).where(Member.user == request.user, Member.organization == request.state.organization),
        HTTPException(403, "Not a member."),
    )


CurrentMember = typing.Annotated[Member, _fetch_current_member]
