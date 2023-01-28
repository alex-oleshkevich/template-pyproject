import typing

from kupala.requests import Request

from {{cookiecutter.project_name}}.config.templating import templates
from {{cookiecutter.project_name}}.organizations.service import get_current_organization


@templates.context_processor
def organization_processors(request: Request) -> dict[str, typing.Any]:
    return {
        "organization": get_current_organization(request),
    }
