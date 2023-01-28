import wtforms
from kupala.contrib.forms import AsyncForm
from starlette_babel import gettext_lazy as _


class LoginForm(AsyncForm):
    email = wtforms.EmailField(label=_("Email"), validators=[wtforms.validators.data_required()])
    password = wtforms.PasswordField(label=_("Password"), validators=[wtforms.validators.data_required()])
    remember_me = wtforms.BooleanField(label=_("Remember me"), default=False)
