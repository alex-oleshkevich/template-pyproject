import dataclasses


@dataclasses.dataclass
class MenuItem:
    label: str
    path_name: str
    icon: str = ""
    path_params: dict[str, str | int] = dataclasses.field(default_factory=dict)
    exact: bool = False
