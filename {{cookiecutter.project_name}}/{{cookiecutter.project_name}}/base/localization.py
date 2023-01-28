from starlette_babel import get_translator

from {{cookiecutter.project_name}}.config.settings import settings


def setup_translator() -> None:
    translator = get_translator()
    translator.load_from_directories([settings.package_dir / "locales"])
