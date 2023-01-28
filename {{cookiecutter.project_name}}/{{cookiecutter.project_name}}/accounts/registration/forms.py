import wtforms
from kupala.contrib.forms import AsyncForm
from starlette_babel import gettext_lazy as _

from {{cookiecutter.project_name}}.accounts.validators import not_same_as_email
from {{cookiecutter.project_name}}.models.users import User


class RegisterAsyncForm(AsyncForm):
    first_name = wtforms.StringField(label=_("First name"), default="")
    last_name = wtforms.StringField(label=_("Last name"), default="")
    email = wtforms.EmailField(label=_("Email"), validators=[wtforms.validators.DataRequired()])
    password = wtforms.PasswordField(
        label=_("Password"),
        validators=[
            wtforms.validators.data_required(),
            wtforms.validators.length(min=8, max=160),
            not_same_as_email,
        ],
    )
    terms = wtforms.BooleanField(
        label=_("Accept usage terms and privacy policy"),
        validators=[wtforms.validators.data_required()],
        render_kw={"class": "form-check-input"},
    )

    async def validate_async_email(self, form: AsyncForm, field: wtforms.Field) -> None:
        if await User.get_by_email(form.context["dbsession"], field.data):
            raise wtforms.ValidationError(_("This address is not available."))
