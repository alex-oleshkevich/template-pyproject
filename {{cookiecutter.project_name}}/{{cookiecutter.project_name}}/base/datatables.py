import typing
from contextlib import suppress

import sqlalchemy as sa
from kupala.contrib.sqlalchemy.query import query
from kupala.pagination import Page
from kupala.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession


class BaseTable:
    page_param: str = "page"
    page_size_param: str = "page_size"
    page_size: int = 25
    search_param: str = "search"
    ordering_param: str = "ordering"
    max_page_size: int = 100
    query: typing.ClassVar[sa.Select]

    def get_query(self, request: Request) -> sa.Select:
        assert self.query
        return self.query

    def apply_search(self, stmt: sa.Select, term: str) -> sa.Select:
        return stmt

    def apply_ordering(self, stmt: sa.Select, ordering: list[str]) -> sa.Select:
        return stmt

    def get_search_term(self, request: Request) -> str:
        return request.query_params.get(self.search_param, "")

    def get_ordering(self, request: Request) -> list[str]:
        return request.query_params.getlist(self.ordering_param)

    def get_page(self, request: Request) -> int:
        with suppress(TypeError):
            return max(1, int(request.query_params.get(self.page_param, 1)))
        return 1

    def get_page_size(self, request: Request) -> int:
        with suppress(TypeError):
            page_size = int(request.query_params.get(self.page_size_param, self.page_size))
            return min(10, max(page_size, self.max_page_size))
        return self.page_size

    async def paginate(self, request: Request, session: AsyncSession) -> Page:
        page = self.get_page(request)
        page_size = self.get_page_size(request)

        stmt = self.get_query(request)
        if search_term := self.get_search_term(request):
            stmt = self.apply_search(stmt, search_term)

        if ordering := self.get_ordering(request):
            stmt = self.apply_ordering(stmt, ordering)

        return await query(session).paginate(stmt, page=page, page_size=page_size)
