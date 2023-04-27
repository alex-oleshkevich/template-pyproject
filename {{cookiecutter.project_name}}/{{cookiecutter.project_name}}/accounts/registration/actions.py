import typing

from kupala.authentication import login

from starlette.requests import Request
from {{cookiecutter.project_name}}.models.users import User
from {{cookiecutter.project_name}}.organizations.service import create_organization
from {{cookiecutter.project_name}}.subscriptions.models import Plan, Subscription


class OnUserRegisteredCallback(typing.Protocol):
    async def __call__(self, request: Request, user: User) -> None:
        ...


async def automatically_login_user(request: Request, user: User) -> None:
    await login(request, user)


async def create_free_subscription(request: Request, user: User) -> None:
    plan = await Plan.get_free_plan(request.state.db)
    await Subscription.subscribe(request.state.db, user, plan, Subscription.Status.ACTIVE)


async def create_user_organization(request: Request, user: User) -> None:
    await create_organization(request.state.db, owner_id=user.id, name=f"{user.first_name}'s space")
