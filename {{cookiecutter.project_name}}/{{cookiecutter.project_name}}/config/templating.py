import typing

import tabler_icons
from kupala.templating import Jinja2Templates, app_processor, url_processors
from starlette.requests import Request
from starlette_babel.contrib.jinja import configure_jinja_env
from starlette_flash.flash import flash_processor

from {{cookiecutter.project_name}}.config.settings import settings
from {{cookiecutter.project_name}}.organizations.service import get_current_organization

context_processors = [
    app_processor,
    url_processors,
    flash_processor,
]

jinja_globals = {
    "tabler_icon": tabler_icons.tabler_icon,
}

templates = Jinja2Templates(
    template_dir=[f"{settings.package_dir}/*/templates"],
    packages=[
        settings.package_name,
        "kupala.contrib.mail",
        "kupala.contrib.forms",
    ],
    context_processors=context_processors,
    globals=jinja_globals,
    plugins=[configure_jinja_env],
)


@templates.context_processor
def organization_processors(request: Request) -> dict[str, typing.Any]:
    return {
        "organization": get_current_organization(request),
    }
