import tabler_icons
from kupala.templating import Jinja2Templates, app_processor, url_processors
from starlette_babel.contrib.jinja import configure_jinja_env
from starlette_flash.flash import flash_processor

from {{cookiecutter.project_name}}.config.settings import settings

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
