import typing

import wtforms
from ohmyadmin import display
from ohmyadmin.display import DisplayField
from ohmyadmin.ext.sqla import SQLAlchemyResource
from starlette.requests import Request

from {{cookiecutter.project_name}}.models.users import User


class UserResource(SQLAlchemyResource):
    icon = "users"
    entity_class = User

    def get_list_fields(self) -> typing.Iterable[DisplayField]:
        yield DisplayField("avatar", component=display.Image())
        yield DisplayField(
            "display_name", sortable=True, sort_by="last_name", searchable=True, search_in="last_name", link=True
        )
        yield DisplayField("email", sortable=True, searchable=True)
        yield DisplayField("joined_at", component=display.DateTime())
        yield DisplayField("active", component=display.Boolean())

    def get_form_fields(self, request: Request) -> typing.Iterable[wtforms.Field]:
        yield wtforms.StringField(name="first_name")
        yield wtforms.StringField(name="last_name")
        yield wtforms.EmailField(name="email")
        yield wtforms.BooleanField(name="active")
