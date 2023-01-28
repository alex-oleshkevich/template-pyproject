import wtforms
from kupala.contrib.forms import AsyncForm
from starlette_babel import gettext_lazy as _


class ForgotPasswordForm(AsyncForm):
    email = wtforms.EmailField(
        label=_("Email"),
        render_kw={"class": "form-control", "autocomplete": "off"},
        validators=[wtforms.validators.DataRequired()],
    )


class ChangePasswordForm(AsyncForm):
    password = wtforms.PasswordField(
        label=_("Password"),
        render_kw={"class": "form-control", "autocomplete": "new-password"},
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(min=8, max=160),
        ],
    )
    password_confirmation = wtforms.PasswordField(
        label=_("Confirm Password"),
        render_kw={"class": "form-control", "autocomplete": "new-password"},
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.EqualTo("password", _("Passwords did not match.")),
        ],
    )
