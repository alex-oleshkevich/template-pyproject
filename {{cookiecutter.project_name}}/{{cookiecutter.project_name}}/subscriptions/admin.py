import typing

import wtforms
from ohmyadmin.display import DisplayField
from ohmyadmin.ext.sqla import SQLAlchemyResource
from starlette.requests import Request
from starlette_babel import gettext_lazy as _

from {{cookiecutter.project_name}}.subscriptions.models import Plan
from {{cookiecutter.project_name}}.subscriptions.packages import get_packages


class PlanResource(SQLAlchemyResource):
    icon = "cash"
    entity_class = Plan

    def get_list_fields(self) -> typing.Iterable[DisplayField]:
        yield DisplayField("name", link=True, label=_("Name"), sortable=True, searchable=True)
        yield DisplayField("description", label=_("Description"))
        yield DisplayField("package", label=_("Package"))

    def get_form_fields(self, request: Request) -> typing.Iterable[wtforms.Field]:
        yield wtforms.StringField(name="name", label=_("Plan name"))
        yield wtforms.TextAreaField(name="description", label=_("Description"))
        yield wtforms.SelectField(
            name="package", choices=[(package.name, package.description) for package in get_packages()]
        )
