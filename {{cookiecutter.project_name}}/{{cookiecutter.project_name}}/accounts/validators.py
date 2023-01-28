import wtforms
from starlette_babel import gettext_lazy as _


def not_same_as_email(form: wtforms.Form, field: wtforms.Form) -> None:
    if field.data.lower() == form.email.data:
        raise wtforms.ValidationError(_("Password must not be the same as email."))
