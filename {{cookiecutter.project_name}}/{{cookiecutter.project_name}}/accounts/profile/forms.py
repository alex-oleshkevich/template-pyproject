import wtforms
from starlette_babel import gettext_lazy as _


class EditProfileForm(wtforms.Form):
    first_name = wtforms.StringField(label=_("First name"))
    last_name = wtforms.StringField(label=_("Last name"))


class ChangePasswordForm(wtforms.Form):
    current_password = wtforms.PasswordField(validators=[wtforms.validators.DataRequired()])
    password = wtforms.PasswordField(
        validators=[wtforms.validators.DataRequired(), wtforms.validators.Length(min=6)],
    )
    confirm_password = wtforms.PasswordField(
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(min=6),
            wtforms.validators.EqualTo("password"),
        ],
    )
