from __future__ import annotations

import functools

from kupala.contrib.mail import Mails
from mailers import Mailer
from mailers.preprocessors.cssliner import css_inliner

from {{cookiecutter.project_name}}.config import templating
from {{cookiecutter.project_name}}.config.settings import settings

default_mailer = Mailer(
    settings.mail.url,
    from_address=f"{settings.mail.from_name} <{settings.mail.from_email}>",
    preprocessors=[css_inliner],
)
mails = Mails({"default": default_mailer}, jinja_env=templating.templates.env)

send_mail = mails.send_mail
get_mailer = functools.partial(mails.get_mailer, "default")
send_templated_mail = mails.send_templated_mail
