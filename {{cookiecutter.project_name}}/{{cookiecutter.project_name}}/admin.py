from ohmyadmin.app import OhMyAdmin
from ohmyadmin.authentication import BaseAuthPolicy
from starlette.authentication import BaseUser
from starlette.requests import Request

from {{cookiecutter.project_name}}.accounts.admin import UserResource
from {{cookiecutter.project_name}}.models.users import User
from {{cookiecutter.project_name}}.subscriptions.admin import PlanResource


class AuthPolicy(BaseAuthPolicy):
    async def authenticate(self, conn: Request, identity: str, password: str) -> BaseUser | None:
        user = await User.get_by_email(conn.state.dbsession, identity)
        if user and user.check_password(password):
            return user

        return None

    async def load_user(self, conn: Request, user_id: str) -> BaseUser | None:
        return conn.auth.user


admin = OhMyAdmin(
    auth_policy=AuthPolicy(),
    pages=[
        UserResource(),
        PlanResource(),
    ],
)
