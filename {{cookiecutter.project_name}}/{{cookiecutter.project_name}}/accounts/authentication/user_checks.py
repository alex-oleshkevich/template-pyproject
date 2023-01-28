import typing

from starlette.requests import Request
from starlette_babel import gettext_lazy as _

from {{cookiecutter.project_name}}.accounts.authentication.exceptions import DisabledAccountError
from {{cookiecutter.project_name}}.models.users import User


class UserCheck(typing.Protocol):
    async def __call__(self, request: Request, user: User) -> None:
        ...


async def reject_disabled_users(request: Request, user: User) -> None:
    if not user.active:
        raise DisabledAccountError(_("This account is disabled."))
