import dataclasses
import os.path
import typing

import click
from kupala.console import printer

from {{cookiecutter.project_name}}.config.settings import secret, env_file, get_settings

settings_commands = click.Group("settings")


def print_variable(var_name: str, value: typing.Any) -> None:
    click.secho('{file} = {value}'.format(
        file=click.style(var_name, fg='blue'),
        value=click.style(value, fg='magenta')
    ))


@settings_commands.command(name="show")
@click.argument("paths", nargs=-1)
def show_settings_command(paths: list[str]) -> None:
    settings = get_settings()
    printer.header("Setting files")
    print_variable(".env", os.path.realpath(env_file))
    print_variable("secrets_dir", os.path.realpath(secret.directory))
    printer.print("")

    printer.header("Configuration object")

    if not paths:
        paths = [""]

    for path in paths:
        nodes = path.split(".")
        current = settings
        if path:
            for node in nodes:
                current = getattr(current, node)

        if dataclasses.is_dataclass(current):
            printer.dump(current)
        else:
            printer.print_variable(path, current)


@settings_commands.command(name="env")
@click.argument("envvar", nargs=-1)
def get_envvar_command(envvar: list[str]) -> None:
    printer.header("Setting files")
    print_variable(".env", os.path.realpath(env_file))
    printer.print("")
    printer.header("Variables")
    for var_name in envvar:
        printer.print_variable(var_name, os.environ.get(var_name))


@settings_commands.command(name="secrets")
def get_secret_command() -> None:
    printer.header("Setting files")
    print_variable(".env", os.path.realpath(env_file))
    print_variable("secrets_dir", os.path.realpath(secret.directory))
    printer.print("")
    printer.header("Secret files")

    for file in os.listdir(secret.directory):
        if file.startswith("."):
            continue

        with open(os.path.join(secret.directory, file), encoding="utf8") as f:
            print_variable(file, f.read())
