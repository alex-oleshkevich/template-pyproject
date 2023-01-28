import anyio
import click
from kupala.console import async_command

from {{cookiecutter.project_name}}.base.storages import get_file_storage

storage_commands = click.Group("storage")


@storage_commands.command("fetch")
@click.option("--storage", default="__default__")
@click.argument("source_file")
@click.argument("local_file")
@async_command
async def fetch_file_command(source_file: str, local_file: str, storage: str) -> None:
    file_storage = get_file_storage(storage)
    await file_storage.write(local_file, await file_storage.open(source_file))


@storage_commands.command("upload")
@click.option("--storage", default="__default__")
@click.argument("local_file")
@click.argument("source_file")
@async_command
async def upload_file_command(source_file: str, local_file: str, storage: str) -> None:
    file_storage = get_file_storage(storage)
    async with await anyio.open_file(local_file, "rb") as f:
        await file_storage.write(source_file, f)


@storage_commands.command("url")
@click.option("--storage", default="__default__")
@click.argument("remote_file")
@async_command
async def url_to_file_command(remote_file: str, storage: str) -> None:
    file_storage = get_file_storage(storage)
    click.secho(await file_storage.url(remote_file))
