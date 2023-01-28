from ohmyadmin.app import OhMyAdmin
from ohmyadmin.auth import BaseAuthPolicy, UserLike, UserMenu
from ohmyadmin.ext.sqla import DbSessionMiddleware
from starlette.middleware import Middleware
from starlette.requests import HTTPConnection

from {{cookiecutter.project_name}}.accounts.admin import UserResource
from {{cookiecutter.project_name}}.config.database import async_session
from {{cookiecutter.project_name}}.models.users import User
from {{cookiecutter.project_name}}.subscriptions.admin import PlanResource


class AuthPolicy(BaseAuthPolicy):
    async def authenticate(self, conn: HTTPConnection, identity: str, password: str) -> UserLike | None:
        user = await User.get_by_email(conn.state.dbsession, identity)
        if user and user.check_password(password):
            return user

        return None

    async def load_user(self, conn: HTTPConnection, user_id: str) -> UserLike | None:
        return conn.auth.user

    def get_user_menu(self, conn: HTTPConnection) -> UserMenu:
        if conn.user.is_authenticated:
            return UserMenu(user_name=str(conn.user), avatar=conn.user.avatar)
        return super().get_user_menu(conn)


admin = OhMyAdmin(
    auth_policy=AuthPolicy(),
    resources=[
        UserResource(),
        PlanResource(),
    ],
    middleware=[
        Middleware(DbSessionMiddleware, dbsession=async_session),
    ],
)
