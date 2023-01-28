import typing

from async_storages import FileStorage

from {{cookiecutter.project_name}}.base.storages import get_file_storage
from {{cookiecutter.project_name}}.config.settings import Settings as _Settings
from {{cookiecutter.project_name}}.config.settings import get_settings
from {{cookiecutter.project_name}}.models.organizations import Organization

Settings = typing.Annotated[_Settings, lambda: get_settings()]
CurrentOrganization = typing.Annotated[Organization, lambda request: request.state.organization]
DefaultFileStorage = typing.Annotated[FileStorage, lambda: get_file_storage()]
