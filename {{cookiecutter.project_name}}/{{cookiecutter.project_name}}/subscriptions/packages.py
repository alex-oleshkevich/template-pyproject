import dataclasses

from {{cookiecutter.project_name}}.subscriptions.features import Feature


@dataclasses.dataclass
class Package:
    name: str
    description: str
    features: list[Feature]


FREE_PACKAGE = Package("free", "Free", [])


def get_packages() -> list[Package]:
    return [
        FREE_PACKAGE,
    ]
