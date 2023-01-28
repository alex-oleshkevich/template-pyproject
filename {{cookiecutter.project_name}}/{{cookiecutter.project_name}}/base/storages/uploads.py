import typing

from async_storages import FileStorage
from kupala.storages import generate_file_name
from starlette.datastructures import UploadFile

UploadFilename = typing.Callable[[UploadFile], str]


async def upload_file(
    path: str,
    upload: UploadFile,
    storage: FileStorage,
    extra_tokens: dict["str", typing.Any] | None = None,
) -> str:
    file_name = generate_file_name(upload, path, extra_tokens)
    await storage.write(file_name, upload)
    return file_name
