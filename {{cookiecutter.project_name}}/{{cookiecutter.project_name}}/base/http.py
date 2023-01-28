from kupala.requests import Request, is_submitted
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.authentication import AuthCredentials
from starlette.datastructures import State
from starlette_flash.flash import FlashBag, flash

from {{cookiecutter.project_name}}.models.organizations import Organization
from {{cookiecutter.project_name}}.models.users import User


class RequestState(State):
    db: AsyncSession
    organization: Organization


class HttpRequest(Request):
    state: RequestState
    user: User
    auth: AuthCredentials

    @property
    def flash(self) -> FlashBag:
        return flash(self)

    @property
    def is_submitted(self) -> bool:
        return is_submitted(self)
