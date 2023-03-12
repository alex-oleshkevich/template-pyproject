import sqlalchemy as sa
import wtforms
from ohmyadmin.contrib.sqlalchemy import SQLADataSource
from ohmyadmin.formatters import AvatarFormatter, BoolFormatter, DateFormatter
from ohmyadmin.resources import Resource
from ohmyadmin.views.table import TableColumn

from {{cookiecutter.project_name}}.models.users import User


class UserForm(wtforms.Form):
    first_name = wtforms.StringField()
    last_name = wtforms.StringField()
    email = wtforms.EmailField(validators=[wtforms.validators.data_required()])
    active = wtforms.BooleanField()


class UserResource(Resource):
    icon = "users"
    datasource = SQLADataSource(User, sa.select(User).order_by(User.joined_at.desc()))
    form_class = UserForm
    columns = [
        TableColumn("avatar", formatter=AvatarFormatter()),
        TableColumn("display_name", sort_by="last_name", sortable=True, searchable=True, search_in="last_name"),
        TableColumn("email", searchable=True),
        TableColumn("active", formatter=BoolFormatter()),
        TableColumn("joined_at", formatter=DateFormatter()),
    ]
