import wtforms
from ohmyadmin.contrib.sqlalchemy import SQLADataSource
from ohmyadmin.resources import Resource
from ohmyadmin.views.table import TableColumn
from starlette_babel import gettext_lazy as _

from {{cookiecutter.project_name}}.subscriptions.models import Plan
from {{cookiecutter.project_name}}.subscriptions.packages import get_packages


class PlanForm(wtforms.Form):
    name = wtforms.StringField(label=_("Plan name"))
    description = wtforms.TextAreaField()
    package = wtforms.SelectField(choices=[(package.name, package.description) for package in get_packages()])


class PlanResource(Resource):
    icon = "cash"
    datasource = SQLADataSource(Plan)
    form_class = PlanForm
    columns = [
        TableColumn("name", link=True, sortable=True, searchable=True),
        TableColumn("description"),
        TableColumn("package"),
    ]
