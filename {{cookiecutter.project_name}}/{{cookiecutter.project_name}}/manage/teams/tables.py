import sqlalchemy as sa
from kupala.requests import Request
from sqlalchemy.orm import joinedload

from {{cookiecutter.project_name}}.base.datatables import BaseTable
from {{cookiecutter.project_name}}.models.organizations import Member
from {{cookiecutter.project_name}}.models.users import User


class TeamTable(BaseTable):
    def apply_search(self, stmt: sa.Select, term: str) -> sa.Select:
        return stmt.where(User.email.ilike(f"%{term}%") | User.last_name.istartswith(term))

    def get_query(self, request: Request) -> sa.Select:
        return (
            sa.Select(Member)
            .join(Member.user)
            .options(joinedload(Member.user))
            .where(Member.organization == request.state.organization)
            .order_by(User.last_name)
        )
