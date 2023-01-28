import wtforms
from kupala.contrib.forms import AsyncForm
from starlette_babel import gettext_lazy as _
from timezones import zones

import {{cookiecutter.project_name}}.base.forms


class CreateOrganizationForm(AsyncForm):
    name = wtforms.StringField(_("Name"), validators=[wtforms.validators.data_required()])
    support_phone = wtforms.StringField(_("Phone"), description=_("Students can use this phone to contact you."))
    support_email = wtforms.StringField(_("Email"), description=_("Students can use this email to contact you."))
    timezone = wtforms.SelectField(
        _("Timezone"), choices=[(name, formatted) for _, name, formatted in zones.get_timezones()]
    )
    logo = {{cookiecutter.project_name}}.base.forms.AsyncFileField(_("Logo"), upload_to="organizations/{pk}/logo_{prefix}_{file_name}")
